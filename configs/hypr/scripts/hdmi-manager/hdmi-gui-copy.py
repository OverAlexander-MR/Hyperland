#!/usr/bin/env python3
# hdmi-gui.py
# Interfaz gráfica para gestión de monitor externo en Hyprland
# Requiere: python-gobject (gtk4 o gtk3), hyprctl

import gi
import subprocess
import json
import os
import sys
import signal
import threading
import time

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango

LOCK_FILE = '/tmp/hdmi-manager.lock'
CONFIG_DIR = os.path.expanduser('~/.config/hypr/scripts/hdmi-manager')
LOG_FILE = os.path.expanduser('~/.local/share/hdmi-manager/hdmi-manager.log')

# ─── Colores y estilos CSS ───────────────────────────────────────────────────
CSS = """
* {
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
}

window {
    background-color: #0d0f14;
}

.main-container {
    background-color: #0d0f14;
    padding: 32px;
}

.header-title {
    font-size: 22px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: 2px;
}

.header-subtitle {
    font-size: 11px;
    color: #4a5568;
    letter-spacing: 3px;
}

.monitor-badge {
    background-color: #1a1d26;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 12px 16px;
}

.monitor-name {
    font-size: 13px;
    font-weight: 600;
    color: #63b3ed;
}

.monitor-res {
    font-size: 11px;
    color: #718096;
}

.section-label {
    font-size: 10px;
    font-weight: 700;
    color: #4a5568;
    letter-spacing: 3px;
}

/* Botones de modo */
.mode-btn {
    background-color: #1a1d26;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 20px 16px;
    color: #a0aec0;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    transition: all 200ms ease;
    min-width: 140px;
    min-height: 100px;
}

.mode-btn:hover {
    background-color: #1e2233;
    border-color: #4299e1;
    color: #e2e8f0;
}

.mode-btn.selected {
    background-color: #162032;
    border: 2px solid #4299e1;
    color: #63b3ed;
}

.mode-icon {
    font-size: 28px;
}

/* Botones de dirección */
.dir-btn {
    background-color: #1a1d26;
    border: 1px solid #2d3748;
    border-radius: 8px;
    color: #718096;
    font-size: 18px;
    min-width: 52px;
    min-height: 52px;
    transition: all 150ms ease;
}

.dir-btn:hover {
    background-color: #1e2233;
    border-color: #4299e1;
    color: #e2e8f0;
}

.dir-btn.selected {
    background-color: #162032;
    border: 2px solid #4299e1;
    color: #63b3ed;
}

.dir-center {
    background-color: #111318;
    border: 1px solid #2d3748;
    border-radius: 8px;
    color: #2d3748;
    font-size: 11px;
    min-width: 52px;
    min-height: 52px;
}

/* Dropdown de resolución */
.res-combo {
    background-color: #1a1d26;
    border: 1px solid #2d3748;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 12px;
    padding: 8px 12px;
    min-width: 240px;
}

/* Botón aplicar */
.apply-btn {
    background-color: #1a56a0;
    border: none;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 14px 32px;
    min-width: 200px;
    transition: all 200ms ease;
}

.apply-btn:hover {
    background-color: #2563c4;
}

.apply-btn:disabled {
    background-color: #1a1d26;
    color: #4a5568;
}

.cancel-btn {
    background-color: transparent;
    border: 1px solid #2d3748;
    border-radius: 8px;
    color: #718096;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 14px 24px;
    transition: all 200ms ease;
}

.cancel-btn:hover {
    border-color: #e53e3e;
    color: #fc8181;
}

.status-bar {
    background-color: #0a0c10;
    border-top: 1px solid #1a1d26;
    padding: 8px 16px;
}

.status-text {
    font-size: 10px;
    color: #4a5568;
    letter-spacing: 1px;
}

.divider {
    background-color: #1a1d26;
    min-height: 1px;
}

.save-check {
    color: #718096;
    font-size: 11px;
}

.save-check check {
    background-color: #1a1d26;
    border-color: #2d3748;
    border-radius: 4px;
}

.save-check check:checked {
    background-color: #1a56a0;
    border-color: #4299e1;
}
"""

def log(msg):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] GUI: {msg}\n")


# ─── Helpers Hyprland ────────────────────────────────────────────────────────

def get_monitors():
    """Obtiene información de monitores via hyprctl."""
    try:
        result = subprocess.run(['hyprctl', 'monitors', 'all','-j'],
                                capture_output=True, text=True, timeout=5)
        return json.loads(result.stdout)
    except Exception as e:
        log(f"Error obteniendo monitores: {e}")
        return []


def get_connected_monitors():
    monitors = get_monitors()
    return [
        m for m in monitors
        if not m.get('disabled', False)
    ]

def get_external_monitors(monitors):
    """Filtra monitores externos (cualquiera que no sea el principal)."""
    primary = get_primary_monitor(monitors)
    if not primary:
        return monitors[1:] if len(monitors) > 1 else []
    return [m for m in monitors if m['name'] != primary['name']]


def get_primary_monitor(monitors):
    """Obtiene el monitor principal (generalmente eDP/LVDS/built-in)."""
    for m in monitors:
        name = m.get('name', '').upper()
        if any(k in name for k in ['EDP', 'LVDS', 'DSI', 'INTERNAL']):
            return m
    return monitors[0] if monitors else None


def get_available_resolutions(monitor_name):
    """Obtiene resoluciones disponibles para un monitor."""
    try:
        result = subprocess.run(['hyprctl', 'monitors', '-j'],
                                capture_output=True, text=True, timeout=5)
        monitors = json.loads(result.stdout)
        for m in monitors:
            if m['name'] == monitor_name:
                modes = m.get('availableModes', [])
                if modes:
                    # Ordenar por resolución (mayor primero)
                    def res_key(mode):
                        try:
                            res = mode.split('@')[0] if '@' in mode else mode
                            w, h = res.split('x')
                            return int(w) * int(h)
                        except:
                            return 0
                    return sorted(modes, key=res_key, reverse=True)
    except Exception as e:
        log(f"Error obteniendo resoluciones: {e}")

    # Resoluciones comunes como fallback
    return ['3840x2160@60Hz', '2560x1440@144Hz', '2560x1440@60Hz',
            '1920x1080@144Hz', '1920x1080@60Hz', '1280x720@60Hz']


def apply_mirror(primary, external):
    """Configura espejo de pantalla según ejemplo del usuario."""
    primary_name = primary['name']
    external_name = external['name']
    primary_res = f"{primary['width']}x{primary['height']}@{primary.get('refreshRate', 60):.2f}"

    # Ejemplo del usuario: 
    # monitor=eDP-1,1920x1080@60,0x1080,1
    # monitor = HDMI-A-1, preferred, auto, 1, mirror, eDP-1
    cmd1 = f"hyprctl keyword monitor {primary_name},{primary_res},0x1080,1"
    cmd2 = f"hyprctl keyword monitor {external_name},preferred,auto,1,mirror,{primary_name}"
    
    log(f"Ejecutando: {cmd1}")
    subprocess.run(cmd1.split(), capture_output=True, text=True)
    log(f"Ejecutando: {cmd2}")
    return subprocess.run(cmd2.split(), capture_output=True, text=True)


def apply_extend(primary, external, resolution, direction):
    """Configura extensión de pantalla con Externo en 0x0."""
    primary_name = primary['name']
    external_name = external['name']

    p_width = primary.get('width', 1920)
    p_height = primary.get('height', 1080)
    
    # Parsear resolución seleccionada
    res_clean = resolution.split('@')[0] if '@' in resolution else resolution
    try:
        ext_w, ext_h = map(int, res_clean.split('x'))
    except:
        ext_w, ext_h = 1920, 1080

    # Seguir el ejemplo del usuario: Externo siempre en 0x0
    # Ejemplo Right: HDMI en 0x0, eDP-1 en -1920x0
    e_pos = "0x0"
    
    if direction == 'right':
        p_pos = f"-{p_width}x0"
    elif direction == 'left':
        p_pos = f"{ext_w}x0"
    elif direction == 'above':
        p_pos = f"0x{ext_h}"
    elif direction == 'below':
        p_pos = f"0x-{p_height}"
    else:
        p_pos = f"-{p_width}x0"

    # Frecuencia de refresco para externo
    rate = resolution.split('@')[1].replace('Hz', '') if '@' in resolution else '60'
    ext_full_res = f"{res_clean}@{rate}"
    
    # Frecuencia de refresco para primario
    p_rate = f"{primary.get('refreshRate', 60):.2f}"
    p_full_res = f"{p_width}x{p_height}@{p_rate}"

    # Aplicar ambos
    cmd_e = f"hyprctl keyword monitor {external_name},{ext_full_res},{e_pos},1"
    cmd_p = f"hyprctl keyword monitor {primary_name},{p_full_res},{p_pos},1"
    
    log(f"Ejecutando: {cmd_e}")
    subprocess.run(cmd_e.split(), capture_output=True, text=True)
    log(f"Ejecutando: {cmd_p}")
    return subprocess.run(cmd_p.split(), capture_output=True, text=True)

def save_to_hyprland_conf(primary, external, mode, resolution=None, direction=None):
    conf_path = os.path.expanduser('~/.config/hypr/hyprland.conf')
    if not os.path.exists(conf_path):
        log(f"No se encontró {conf_path}")
        return False

    try:
        with open(conf_path, 'r') as f:
            lines = f.readlines()

        marker = "# Monitor configuration via HDMI Manager\n"

        # ── Generar nuevas líneas ──
        p_width = primary.get('width', 1920)
        p_height = primary.get('height', 1080)
        p_rate = f"{primary.get('refreshRate', 60):.2f}"
        p_full_res = f"{p_width}x{p_height}@{p_rate}"

        if mode == 'mirror':
            p_conf = f"monitor = {primary['name']},{p_full_res},0x1080,1\n"
            e_conf = f"monitor = {external['name']},preferred,auto,1,mirror,{primary['name']}\n"
        else:
            res_clean = resolution.split('@')[0] if resolution and '@' in resolution else (resolution or '1920x1080')
            rate = resolution.split('@')[1].replace('Hz', '') if resolution and '@' in resolution else '60'
            ext_full_res = f"{res_clean}@{rate}"

            try:
                ext_w, ext_h = map(int, res_clean.split('x'))
            except:
                ext_w, ext_h = 1920, 1080

            if direction == 'right':
                p_pos = f"-{p_width}x0"
            elif direction == 'left':
                p_pos = f"{ext_w}x0"
            elif direction == 'above':
                p_pos = f"0x{ext_h}"
            else:
                p_pos = f"0x-{p_height}"

            e_conf = f"monitor = {external['name']},{ext_full_res},0x0,1\n"
            p_conf = f"monitor = {primary['name']},{p_full_res},{p_pos},1\n"

        new_block = [marker, p_conf, e_conf]

        # ── Buscar si ya existe el bloque ──
        if marker in lines:
            idx = lines.index(marker)

            # Eliminar bloque existente (comentario + 2 líneas siguientes)
            end = idx + 3
            lines = lines[:idx] + lines[end:]

            # Insertar nuevo bloque en la misma posición
            lines[idx:idx] = new_block
        else:
            # Si no existe, añadir al final
            lines.append("\n")
            lines.extend(new_block)

        # ── Guardar ──
        with open(conf_path, 'w') as f:
            f.writelines(lines)

        log("Configuración actualizada.")
        return True

    except Exception as e:
        log(f"Error guardando configuración: {e}")
        return False


# ─── Ventana principal ───────────────────────────────────────────────────────

class HdmiManagerWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="HDMI Manager")
        self.set_default_size(520, -1)
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)

        # Estado
        self.selected_mode = None      # 'mirror' | 'extend'
        self.selected_direction = None # 'right' | 'left' | 'above' | 'below'
        self.selected_resolution = None

        self.monitors = get_connected_monitors() #get_monitors()
        self.external_monitors = get_external_monitors(self.monitors)
        self.primary = get_primary_monitor(self.monitors)
        self.external = self.external_monitors[0] if self.external_monitors else None

        # CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self._build_ui()
        self.connect('destroy', self._on_destroy)
        self.connect('key-press-event', self._on_key)

        # Cerrar con Escape
        self.show_all()
        log(f"Ventana creada. Monitores externos: {[m['name'] for m in self.external_monitors]}")

    def _build_ui(self):
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main.get_style_context().add_class('main-container')
        outer.pack_start(main, True, True, 0)

        # ── Header ──
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title = Gtk.Label(label="HDMI MANAGER")
        title.get_style_context().add_class('header-title')
        title.set_halign(Gtk.Align.START)
        subtitle = Gtk.Label(label="HYPRLAND DISPLAY CONTROLLER")
        subtitle.get_style_context().add_class('header-subtitle')
        subtitle.set_halign(Gtk.Align.START)
        header.pack_start(title, False, False, 0)
        header.pack_start(subtitle, False, False, 0)
        main.pack_start(header, False, False, 0)

        # ── Info de monitores ──
        monitors_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)

        if self.primary:
            p_box = self._make_monitor_badge("🖥", self.primary['name'],
                f"{self.primary.get('width','?')}×{self.primary.get('height','?')} • PRINCIPAL")
            monitors_box.pack_start(p_box, True, True, 0)

        arrow = Gtk.Label(label="⟷")
        arrow.set_markup('<span foreground="#2d3748" size="xx-large">⟷</span>')
        monitors_box.pack_start(arrow, False, False, 0)

        if self.external:
            e_box = self._make_monitor_badge("📺", self.external['name'],
                f"{self.external.get('width','?')}×{self.external.get('height','?')} • HDMI")
            monitors_box.pack_start(e_box, True, True, 0)
        else:
            no_ext = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            no_ext.get_style_context().add_class('monitor-badge')
            lbl = Gtk.Label(label="⚠  Sin monitor externo detectado")
            lbl.get_style_context().add_class('monitor-res')
            no_ext.pack_start(lbl, True, True, 8)
            monitors_box.pack_start(no_ext, True, True, 0)

        main.pack_start(monitors_box, False, False, 0)

        # ── Separador ──
        sep1 = Gtk.Separator()
        sep1.get_style_context().add_class('divider')
        main.pack_start(sep1, False, False, 0)

        # ── Selección de modo ──
        mode_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        mode_label = Gtk.Label(label="MODO DE PANTALLA")
        mode_label.get_style_context().add_class('section-label')
        mode_label.set_halign(Gtk.Align.START)
        mode_section.pack_start(mode_label, False, False, 0)

        mode_buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.btn_mirror = self._make_mode_btn("⊡", "DUPLICAR", "Misma imagen\nen ambas pantallas", 'mirror')
        self.btn_extend = self._make_mode_btn("⊞", "EXTENDER", "Escritorio\nampliado", 'extend')
        mode_buttons.pack_start(self.btn_mirror, True, True, 0)
        mode_buttons.pack_start(self.btn_extend, True, True, 0)
        mode_section.pack_start(mode_buttons, False, False, 0)
        main.pack_start(mode_section, False, False, 0)

        # ── Panel de extensión (oculto inicialmente) ──
        self.extend_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.extend_panel.set_no_show_all(True)

        sep2 = Gtk.Separator()
        sep2.get_style_context().add_class('divider')
        self.extend_panel.pack_start(sep2, False, False, 0)

        # Resolución
        res_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        res_label = Gtk.Label(label="RESOLUCIÓN DEL MONITOR EXTERNO")
        res_label.get_style_context().add_class('section-label')
        res_label.set_halign(Gtk.Align.START)
        res_section.pack_start(res_label, False, False, 0)

        self.res_combo = Gtk.ComboBoxText()
        self.res_combo.get_style_context().add_class('res-combo')
        if self.external:
            resolutions = get_available_resolutions(self.external['name'])
            for r in resolutions:
                self.res_combo.append_text(r)
            if resolutions:
                self.res_combo.set_active(0)
                self.selected_resolution = resolutions[0]
        self.res_combo.connect('changed', self._on_resolution_changed)
        res_section.pack_start(self.res_combo, False, False, 0)
        self.extend_panel.pack_start(res_section, False, False, 0)

        # Dirección
        dir_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        dir_label = Gtk.Label(label="POSICIÓN DEL MONITOR EXTERNO")
        dir_label.get_style_context().add_class('section-label')
        dir_label.set_halign(Gtk.Align.START)
        dir_section.pack_start(dir_label, False, False, 0)

        # Grid de dirección
        dir_center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        dir_center_box.set_halign(Gtk.Align.CENTER)

        # Fila superior (arriba)
        row_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row_top.set_halign(Gtk.Align.CENTER)
        spacer1 = Gtk.Box()
        spacer1.set_size_request(52, 52)
        self.btn_above = self._make_dir_btn("▲", 'above')
        spacer2 = Gtk.Box()
        spacer2.set_size_request(52, 52)
        row_top.pack_start(spacer1, False, False, 0)
        row_top.pack_start(self.btn_above, False, False, 0)
        row_top.pack_start(spacer2, False, False, 0)

        # Fila media (izq / centro / der)
        row_mid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row_mid.set_halign(Gtk.Align.CENTER)
        self.btn_left = self._make_dir_btn("◀", 'left')
        center_lbl = Gtk.Label(label="🖥")
        center_lbl.get_style_context().add_class('dir-center')
        center_lbl.set_size_request(52, 52)
        self.btn_right = self._make_dir_btn("▶", 'right')
        row_mid.pack_start(self.btn_left, False, False, 0)
        row_mid.pack_start(center_lbl, False, False, 0)
        row_mid.pack_start(self.btn_right, False, False, 0)

        # Fila inferior (abajo)
        row_bot = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row_bot.set_halign(Gtk.Align.CENTER)
        spacer3 = Gtk.Box()
        spacer3.set_size_request(52, 52)
        self.btn_below = self._make_dir_btn("▼", 'below')
        spacer4 = Gtk.Box()
        spacer4.set_size_request(52, 52)
        row_bot.pack_start(spacer3, False, False, 0)
        row_bot.pack_start(self.btn_below, False, False, 0)
        row_bot.pack_start(spacer4, False, False, 0)

        dir_center_box.pack_start(row_top, False, False, 0)
        dir_center_box.pack_start(row_mid, False, False, 0)
        dir_center_box.pack_start(row_bot, False, False, 0)

        # Descripción de dirección seleccionada
        self.dir_desc = Gtk.Label(label="Seleccioná una dirección")
        self.dir_desc.get_style_context().add_class('monitor-res')
        self.dir_desc.set_halign(Gtk.Align.CENTER)

        dir_section.pack_start(dir_center_box, False, False, 0)
        dir_section.pack_start(self.dir_desc, False, False, 4)
        self.extend_panel.pack_start(dir_section, False, False, 0)

        main.pack_start(self.extend_panel, False, False, 0)

        # ── Separador final ──
        sep3 = Gtk.Separator()
        sep3.get_style_context().add_class('divider')
        main.pack_start(sep3, False, False, 0)

        # ── Opción guardar ──
        save_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.save_check = Gtk.CheckButton(label="  Guardar en hyprland.conf")
        self.save_check.get_style_context().add_class('save-check')
        self.save_check.set_active(True)
        save_box.pack_start(self.save_check, False, False, 0)
        main.pack_start(save_box, False, False, 0)

        # ── Botones de acción ──
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        action_box.set_halign(Gtk.Align.CENTER)

        btn_cancel = Gtk.Button(label="CANCELAR")
        btn_cancel.get_style_context().add_class('cancel-btn')
        btn_cancel.connect('clicked', lambda _: self.destroy())

        self.btn_apply = Gtk.Button(label="APLICAR")
        self.btn_apply.get_style_context().add_class('apply-btn')
        self.btn_apply.connect('clicked', self._on_apply)
        self.btn_apply.set_sensitive(False)

        action_box.pack_start(btn_cancel, False, False, 0)
        action_box.pack_start(self.btn_apply, False, False, 0)
        main.pack_start(action_box, False, False, 0)

        # ── Status bar ──
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        status_box.get_style_context().add_class('status-bar')
        self.status_label = Gtk.Label(label="● Listo")
        self.status_label.get_style_context().add_class('status-text')
        self.status_label.set_halign(Gtk.Align.START)
        status_box.pack_start(self.status_label, True, True, 0)
        outer.pack_start(status_box, False, False, 0)

    def _make_monitor_badge(self, icon, name, desc):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.get_style_context().add_class('monitor-badge')
        icon_lbl = Gtk.Label()
        icon_lbl.set_markup(f'<span size="xx-large">{icon}</span>')
        name_lbl = Gtk.Label(label=name)
        name_lbl.get_style_context().add_class('monitor-name')
        desc_lbl = Gtk.Label(label=desc)
        desc_lbl.get_style_context().add_class('monitor-res')
        box.pack_start(icon_lbl, False, False, 4)
        box.pack_start(name_lbl, False, False, 0)
        box.pack_start(desc_lbl, False, False, 0)
        return box

    def _make_mode_btn(self, icon, label_text, desc, mode):
        btn = Gtk.Button()
        btn.get_style_context().add_class('mode-btn')
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        icon_lbl = Gtk.Label()
        icon_lbl.set_markup(f'<span size="xx-large">{icon}</span>')
        icon_lbl.get_style_context().add_class('mode-icon')
        lbl = Gtk.Label(label=label_text)
        desc_lbl = Gtk.Label(label=desc)
        desc_lbl.get_style_context().add_class('monitor-res')
        desc_lbl.set_justify(Gtk.Justification.CENTER)
        box.pack_start(icon_lbl, False, False, 0)
        box.pack_start(lbl, False, False, 0)
        box.pack_start(desc_lbl, False, False, 0)
        btn.add(box)
        btn.connect('clicked', self._on_mode_selected, mode)
        return btn

    def _make_dir_btn(self, label_text, direction):
        btn = Gtk.Button(label=label_text)
        btn.get_style_context().add_class('dir-btn')
        btn.set_size_request(52, 52)
        btn.connect('clicked', self._on_direction_selected, direction)
        return btn

    def _on_mode_selected(self, btn, mode):
        self.selected_mode = mode
        # Actualizar estilos
        for b, m in [(self.btn_mirror, 'mirror'), (self.btn_extend, 'extend')]:
            ctx = b.get_style_context()
            if m == mode:
                ctx.add_class('selected')
            else:
                ctx.remove_class('selected')

        # Mostrar/ocultar panel de extensión
        if mode == 'extend':
            self.extend_panel.set_no_show_all(False)
            self.extend_panel.show_all()
        else:
            self.extend_panel.hide()

        self._update_apply_state()

    def _on_direction_selected(self, btn, direction):
        self.selected_direction = direction
        dir_labels = {
            'right': 'Monitor externo a la DERECHA del principal',
            'left':  'Monitor externo a la IZQUIERDA del principal',
            'above': 'Monitor externo ENCIMA del principal',
            'below': 'Monitor externo DEBAJO del principal',
        }
        self.dir_desc.set_text(dir_labels.get(direction, ''))

        for b, d in [(self.btn_right, 'right'), (self.btn_left, 'left'),
                     (self.btn_above, 'above'), (self.btn_below, 'below')]:
            ctx = b.get_style_context()
            if d == direction:
                ctx.add_class('selected')
            else:
                ctx.remove_class('selected')

        self._update_apply_state()

    def _on_resolution_changed(self, combo):
        self.selected_resolution = combo.get_active_text()

    def _update_apply_state(self):
        if self.selected_mode == 'mirror':
            self.btn_apply.set_sensitive(True)
        elif self.selected_mode == 'extend' and self.selected_direction:
            self.btn_apply.set_sensitive(True)
        else:
            self.btn_apply.set_sensitive(False)

    def _on_apply(self, btn):
        if not self.external or not self.primary:
            self._set_status("⚠  No se detectaron monitores")
            return

        self.btn_apply.set_sensitive(False)
        self._set_status("⟳  Aplicando configuración...")

        def do_apply():
            try:
                if self.selected_mode == 'mirror':
                    result = apply_mirror(self.primary, self.external)
                    msg = "✓  Pantalla duplicada correctamente"
                    save_args = (self.primary, self.external, 'mirror', None, None)
                else:
                    result = apply_extend(self.primary, self.external,
                                          self.selected_resolution,
                                          self.selected_direction)
                    dir_names = {'right': 'derecha', 'left': 'izquierda',
                                 'above': 'arriba', 'below': 'abajo'}
                    msg = f"✓  Extendido hacia la {dir_names.get(self.selected_direction,'')}"
                    save_args = (self.primary, self.external, 'extend',
                                 self.selected_resolution, self.selected_direction)

                if result.returncode != 0:
                    msg = f"⚠  Error: {result.stderr.strip()}"
                    log(f"Error aplicando: {result.stderr}")
                elif self.save_check.get_active():
                    saved = save_to_hyprland_conf(*save_args)
                    if saved:
                        msg += " • Guardado en config"

                GLib.idle_add(self._set_status, msg)
                GLib.idle_add(self.btn_apply.set_sensitive, True)

                if result.returncode == 0:
                    GLib.timeout_add(2000, self.destroy)

            except Exception as e:
                log(f"Excepción en apply: {e}")
                GLib.idle_add(self._set_status, f"⚠  Error: {str(e)}")
                GLib.idle_add(self.btn_apply.set_sensitive, True)

        thread = threading.Thread(target=do_apply, daemon=True)
        thread.start()

    def _set_status(self, msg):
        self.status_label.set_text(msg)
        return False

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def _on_destroy(self, widget):
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
        log("Ventana cerrada")
        Gtk.main_quit()


def main():
    # Verificar que hay monitores externos
    monitors = get_connected_monitors() #get_monitors()
    external = get_external_monitors(monitors)
    if not external:
        log("No hay monitores externos conectados, saliendo")
        sys.exit(0)

    signal.signal(signal.SIGTERM, lambda *_: Gtk.main_quit())
    signal.signal(signal.SIGINT, lambda *_: Gtk.main_quit())

    win = HdmiManagerWindow()
    Gtk.main()


if __name__ == '__main__':
    main()
