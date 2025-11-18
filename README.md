<div align="center">
    <h1>Late Night 🌃</h1>
</div>

<div align="center">

![](https://raw.githubusercontent.com/iamverysimp1e/dots/late-night-%F0%9F%8C%83/ScreenShots/HyprLand/preview.png)

</div>

<div align="center">
    <h1>Installations 💫</h1>
</div>

## Dependencies

> Just [R.T.F.M](https://en.wikipedia.org/wiki/RTFM)

- First of all, Install the newest [Hyprland](https://hyprland.org/) using this [guide](https://wiki.hyprland.org/Getting-Started/Installation/) depend on your Distro:

  ```zsh
   sudo pacman -S hyprland hypridle slurp gtklock
  ```

- For all dependencies, install in Manual [(Manual Build Hyperland)](https://wiki.hyprland.org/Getting-Started/Installation/)

### Base setups 💻:

- Install waybar, Rofi, Dunst, kitty terminal, swaybg, swaylock-fancy, swayidle, pamixer, light, Brillo:

```
yay -S waybar rofi dunst kitty swaybg swaylock-fancy-git swayidle pamixer light brillo brightnessctl
```

### Necessary Font 🔑:

- [JetBrains Mono Nerd Font](https://github.com/ryanoasis/nerd-fonts/releases/download/v2.2.2/JetBrainsMono.zip)

- [Iosevka Nerd Font](https://github.com/ryanoasis/nerd-fonts/releases/download/v2.3.3/Iosevka.zip)

- [Font Awesome](https://archlinux.org/packages/community/any/ttf-font-awesome/)
  ```
  yay -S ttf-font-awesome
  ```

Optional Font:

- [NotoColorEmoji](https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf)
- [Codicon](https://github.com/microsoft/vscode-codicons/raw/main/dist/codicon.ttf)

> Or either way, check my [fonts](https://github.com/iamverysimp1e/fonts) repos where i store all of the programming fonts.

Once you download them and unpack them, place them into `~/.fonts` or `~/.local/share/fonts.`

Then run this command for your system to detect the newly installed fonts.

```
fc-cache -fv
```

## Copy Files 💾

```
git clone -b late-night-🌃 https://github.com/OverAlexander-MR/Hyperland.git
cd Hyperland
cp -r ./configs/* ~/.config/
```

> Finally, now you can login with Late Night Hyprland Rice

Congratulations, at this point you successfully have installed Hyprland Late Night Rice 🌃
