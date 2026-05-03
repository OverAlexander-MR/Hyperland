#!/bin/bash

# Define monitor names
INTERNAL="eDP-1"
# Fix syntax error (removed space after =) and made detection more robust
EXTERNAL=$(hyprctl monitors | grep -v "$INTERNAL" | grep "Monitor" | awk '{print $2}' | head -1)

if [ -z "$EXTERNAL" ]; then
    # Fallback to HDMI if not found
    EXTERNAL=$(hyprctl monitors | grep "HDMI" | awk '{print $2}' | head -1)
fi

# Options for Rofi
options="Extend\nMirror\nExternal Only\nInternal Only"

# Get user selection
choice=$(echo -e "$options" | rofi -dmenu -i -p "Monitor Mode:")

case "$choice" in
    "Extend")
        hyprctl keyword monitor "$INTERNAL, 1920x1080@60, 0x1080, 1"
        hyprctl keyword monitor "$EXTERNAL, preferred, 0x0, 1"
        ;;
    "Mirror")
        hyprctl keyword monitor "$INTERNAL, 1920x1080@60, 0x0, 1"
        hyprctl keyword monitor "$EXTERNAL, preferred, 0x0, 1, mirror, $INTERNAL"
        ;;
    "External Only")
        hyprctl keyword monitor "$INTERNAL, disable"
        hyprctl keyword monitor "$EXTERNAL, preferred, 0x0, 1"
        ;;
    "Internal Only")
        hyprctl keyword monitor "$INTERNAL, 1920x1080@60, 0x0, 1"
        hyprctl keyword monitor "$EXTERNAL, disable"
        ;;
esac
