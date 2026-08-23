-- ############################################
-- #  ____  _           _ _
-- # |  _ \(_)         | (_)
-- # | |_) |_ _ __   __| |_ _ __   __ _ ___
-- # |  _ <| | '_ \ / _` | | '_ \ / _` / __|
-- # | |_) | | | | | (_| | | | | | (_| \__ \
-- # |____/|_|_| |_|\__,_|_|_| |_|\__, |___/
-- #                               __/ |
-- #                              |___/
-- #
-- ############################################

local mainMod = "SUPER"

-- Kill active window
hl.bind(mainMod .. " + Q", hl.dsp.window.close())

-- Exit session
hl.bind(mainMod .. " + M", hl.dsp.exit())
-- bind = SUPER,M,exit

-- Lock screen
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("swaylock-fancy"))

-- Fullscreen (maximized)
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" }))

-- Fullscreen (real)
hl.bind(mainMod .. " + SHIFT + F", hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }))

-- Terminal
hl.bind(mainMod .. " + RETURN", hl.dsp.exec_cmd("kitty"))

-- Kill active (duplicate)
hl.bind(mainMod .. " + C", hl.dsp.window.close())

-- Exit session (duplicate)
hl.bind(mainMod .. " + SHIFT + Q", hl.dsp.exec_cmd("uwsm stop"))

-- File manager
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("nautilus"))

-- App launcher
hl.bind(mainMod .. " + D", hl.dsp.exec_cmd("rofi -show drun"))

-- Power menu
hl.bind("XF86PowerOff", hl.dsp.exec_cmd("~/.config/waybar/scripts/power-menu/powermenu.sh"))

-- Clipboard history
hl.bind(mainMod .. " + V", hl.dsp.exec_cmd("cliphist list | wofi --dmenu | cliphist decode | wl-copy"))

-- Wallpaper
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("quickshell -c hyprquickpaper"))

-- Monitors
hl.bind(mainMod .. " + P", hl.dsp.exec_cmd("python3 ~/.config/hypr/scripts/hdmi-manager/hdmi-gui.py"))

-- Audio
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("~/.config/hypr/scripts/volume mute"),  { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd("~/.config/hypr/scripts/volume down"), { locked = true, repeating = true })
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd("~/.config/hypr/scripts/volume up"),   { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",     hl.dsp.exec_cmd("pactl set-source-mute @DEFAULT_SOURCE@ toggle"), { locked = true, repeating = true })

-- Brightness
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("~/.config/hypr/scripts/brightness up"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("~/.config/hypr/scripts/brightness down"), { locked = true, repeating = true })

-- Color picker
hl.bind(mainMod .. " + SHIFT + C", hl.dsp.exec_cmd("bash ~/.config/hypr/scripts/hyprPicker.sh"))

-- Toggle floating
hl.bind(mainMod .. " + T", hl.dsp.window.float({ action = "toggle" }))

-- Screenshot
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("sh -c 'file=~/Pictures/Capturas/$(date +%Y-%m-%d_%H-%M-%S).png; grim -g \"$(slurp)\" \"$file\" && wl-copy < \"$file\"'"))

-- Move focus (vim-style)
hl.bind(mainMod .. " + J", hl.dsp.focus({ direction = "down" }))
hl.bind(mainMod .. " + K", hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + H", hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + L", hl.dsp.focus({ direction = "right" }))

-- Resize active window
hl.bind(mainMod .. " + left",  hl.dsp.window.resize({ x = -40, y = 0,  relative = true }))
hl.bind(mainMod .. " + right", hl.dsp.window.resize({ x = 40,  y = 0,  relative = true }))
hl.bind(mainMod .. " + up",    hl.dsp.window.resize({ x = 0,   y = -40, relative = true }))
hl.bind(mainMod .. " + down",  hl.dsp.window.resize({ x = 0,   y = 40,  relative = true }))

-- Move window (vim-style)
hl.bind(mainMod .. " + SHIFT + H", hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + L", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + K", hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + J", hl.dsp.window.move({ direction = "down" }))

-- Switch workspaces
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key,             hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key,     hl.dsp.window.move({ workspace = i }))
end
