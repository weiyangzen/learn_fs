# sources/sync-backup/syncthing/etc/linux-desktop/syncthing-start.desktop

## Purpose
This desktop entry starts the Syncthing daemon from a Linux desktop session. It is intended for graphical autostart/menu integration rather than system service management.

## Important APIs, Types, And Functions
The file follows the freedesktop `.desktop` entry format. Important keys are `Name=Start Syncthing`, `GenericName=File synchronization`, `Exec=syncthing serve --no-browser --logfile=default`, `Icon=syncthing`, `Terminal=false`, `Type=Application`, `Keywords=synchronization;daemon;`, and `Categories=Network;FileTransfer;P2P`.

## Control Flow
There is no internal control flow. A desktop environment or autostart manager reads the entry and executes the `Exec` command when the user launches it or when it is installed as an autostart item. The command starts Syncthing in serve mode, disables automatic browser opening, and uses Syncthing's default logfile handling.

## State And Persistence Behavior
The desktop file itself persists no runtime state. The launched Syncthing process uses the user's normal home/config/data locations and writes logs according to `--logfile=default`. Because it runs in the user's desktop session, it inherits user environment and permissions.

## Dependencies And Integration Points
The entry depends on `syncthing` being in the desktop session's PATH and on the icon theme/package providing a `syncthing` icon. It complements service templates under `etc/linux-systemd`, `linux-runit`, and `linux-upstart` for users who prefer session startup.

## Risks And Edge Cases
If PATH does not include the Syncthing binary, launch fails silently or with a desktop-specific error. Multiple autostart mechanisms can accidentally start duplicate Syncthing processes. `--no-browser` prevents an unwanted browser window, but users still need separate UI access via the browser command or web URL.

## Test Signals
Desktop-file validation tools can verify syntax. Manual testing should install or open the desktop entry in a Linux desktop session and confirm Syncthing starts in the background without opening a browser.
