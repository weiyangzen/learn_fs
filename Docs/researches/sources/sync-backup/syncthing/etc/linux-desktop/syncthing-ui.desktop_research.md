# sources/sync-backup/syncthing/etc/linux-desktop/syncthing-ui.desktop

## Purpose
This desktop entry opens the Syncthing Web UI from a Linux desktop environment. It assumes the Syncthing daemon is already running.

## Important APIs, Types, And Functions
The file uses standard `.desktop` keys. `Name=Syncthing Web UI`, `GenericName=File synchronization UI`, `Exec=syncthing browser`, `Icon=syncthing`, `Terminal=false`, `Type=Application`, `Keywords=synchronization;interface;`, and `Categories=Network;FileTransfer;P2P` define how desktop launchers present and execute it.

## Control Flow
There is no logic in the file. A desktop launcher executes `syncthing browser`, which delegates to Syncthing's command-line browser-opening path and ultimately the platform-specific `openURL` helper after resolving the GUI URL.

## State And Persistence Behavior
The desktop file does not store state. It may cause the Syncthing command to read local configuration to determine the GUI URL and then launch the user's default browser. It does not start the daemon itself.

## Dependencies And Integration Points
It depends on a working `syncthing` CLI in PATH, a running Syncthing instance, and desktop/browser integration. It pairs with `syncthing-start.desktop`, where one entry starts the background process and this one opens the interface.

## Risks And Edge Cases
If Syncthing is not running, `syncthing browser` may fail or open a URL that is unreachable. Headless or misconfigured browser environments can fail in the platform opener. As with the start desktop entry, PATH assumptions are packaging-sensitive.

## Test Signals
Syntax can be checked with `desktop-file-validate`. Functional testing should launch the entry from a desktop menu and confirm it opens the configured Syncthing Web UI.
