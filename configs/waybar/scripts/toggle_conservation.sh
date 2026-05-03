#!/bin/bash

# Archivo del modo conservación en Lenovo IdeaPad
FILE="/sys/bus/platform/drivers/ideapad_acpi/VPC2004:00/conservation_mode"

# Comprobar si existe
if [ ! -f "$FILE" ]; then
    notify-send "Battery Mode" "No se encontró el archivo de conservación."
    exit 1
fi

# Leer el valor actual
current=$(cat "$FILE")

if [ "$current" -eq 1 ]; then
    # Desactivar modo conservación
    echo 0 | sudo tee "$FILE" > /dev/null
    notify-send "Battery Mode" "Modo conservación DESACTIVADO (carga al 100%)."
else
    # Activar modo conservación
    echo 1 | sudo tee "$FILE" > /dev/null
    notify-send "Battery Mode" "Modo conservación ACTIVADO (limita la carga)."
fi
