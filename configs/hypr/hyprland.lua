-- #########################################################################################
-- # __  __ _       _                 _
-- #|  \/  (_)_ __ (_)_ __ ___   __ _| |
-- #| |\/| | | '_ \| | '_ ` _ \ / _` | |
-- #| |  | | | | | | | | | | | | (_| | |
-- #|_|  |_|_|_| |_|_|_| |_| |_|\__,_|_|
-- #
-- # _   _                  _                 _    ____             __ _
-- #| | | |_   _ _ __  _ __| | __ _ _ __   __| |  / ___|___  _ __  / _(_) __ _ ___
-- #| |_| | | | | '_ \| '__| |/ _` | '_ \ / _` | | |   / _ \| '_ \| |_| |/ _` / __|
-- #|  _  | |_| | |_) | |  | | (_| | | | | (_| | | |__| (_) | | | |  _| | (_| \__ \
-- #|_| |_|\__, | .__/|_|  |_|\__,_|_| |_|\__,_|  \____\___/|_| |_|_| |_|\__, |___/
-- #       |___/|_|                                                      |___/
-- ##########################################################################################

------------------
---- MONITORS ----
------------------

-- Monitor configuration via HDMI Manager
hl.monitor({ output = "eDP-1", mode = "1920x1080@60.00", position = "0x1080", scale = 1 })
hl.monitor({ output = "HDMI-A-1", mode = "1920x1080@60.00", position = "0x0", scale = 1 })

------------------------------------
---- DARK MODE & ENV VARS ----------
------------------------------------

hl.env("GTK_THEME", "Dracula")
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")

-------------------
---- AUTOSTART ----
-------------------

-- Status bar :)
hl.on("hyprland.start", function()
    hl.exec_cmd("waybar")
    hl.exec_cmd("hypridle")
    hl.exec_cmd("hyprctl reload")
    hl.exec_cmd("hyprpaper")
end)

-- Notification
hl.on("hyprland.start", function()
    hl.exec_cmd("dunst")
    hl.exec_cmd("~/.config/quickshell/hyprquickpaper/restore.sh")
end)

-- For keyboard
hl.on("hyprland.start", function()
    hl.exec_cmd("fcitx5 -D")
end)

-- Almacena el historial de texto
hl.on("hyprland.start", function()
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
end)

-- Almacena imagenes
hl.on("hyprland.start", function()
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
end)

-- Disk mount
hl.on("hyprland.start", function()
    hl.exec_cmd("lxqt-policykit-agent")
end)

-- Bluetooth
hl.on("hyprland.start", function()
    hl.exec_cmd("blueman-applet")
end)

-- Screen Sharing
hl.on("hyprland.start", function()
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("~/.config/hypr/scripts/screensharing.sh")
end)

---------------
---- INPUT ----
---------------

hl.config({
    input = {
        kb_layout     = "latam, us",
        kb_options    = "grp:ctrl_space_toggle",
        follow_mouse  = 1,
        force_no_accel = false,
        sensitivity   = 0.5,

        touchpad = {
            natural_scroll = true,
        },
    },
})

---------------------------
---- GESTURES (TOUCHPAD) ---
---------------------------

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace",
})

---------------
---- CURSOR ---
---------------

hl.config({
    cursor = {
        no_hardware_cursors = false,
    },
})

-----------------------
---- LOOK AND FEEL ----
-----------------------

hl.config({
    general = {
        layout         = "dwindle",
        gaps_in        = 5,
        gaps_out       = 10,
        border_size    = 2,

        col = {
            active_border   = "rgba(5e81acff)",
            inactive_border = "rgba(33333366)",
        },
    },

    decoration = {
        rounding = 18,

        blur = {
            enabled = true,
            size    = 3,
            passes  = 1,
        },
    },

    animations = {
        enabled = true,
    },

    master = {
        new_on_top = true,
    },

    misc = {
        disable_hyprland_logo   = true,
        disable_splash_rendering = true,
        mouse_move_enables_dpms  = true,
    },
})

-- Blur for lockscreen
-- blurls=lockscreen  (not available in Lua API yet, kept as reference)

------------------------
---- ANIMATIONS ---------
------------------------

hl.curve("overshot", { type = "bezier", points = { {0.13, 0.99}, {0.29, 1.1} } })

hl.animation({ leaf = "windows",    enabled = true, speed = 4,   bezier = "overshot", style = "popin" })
hl.animation({ leaf = "fade",       enabled = true, speed = 10,  bezier = "default" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 6,   bezier = "overshot", style = "slide" })
hl.animation({ leaf = "border",     enabled = true, speed = 10,  bezier = "default" })

-----------------------
---- WINDOW RULES -----
-----------------------

-- xwayland-video-bridge fixes
hl.window_rule({
    name  = "xwayland-video-bridge-fixes",
    match = { class = "xwaylandvideobridge" },

    no_initial_focus = true,
    no_focus         = true,
    no_anim          = true,
    no_blur          = true,
    max_size         = "1 1",
    opacity          = 0.0,
})

-----------------------
---- KEYBINDINGS ------
-----------------------

require("keybindings")

-- Move/resize windows with mainMod + LMB/RMB and dragging
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })
