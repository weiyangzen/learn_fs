# sources/sync-backup/unison/data/unison-gui.desktop

Purpose: freedesktop desktop-entry metadata for launching the Unison GUI on Linux/Unix desktop environments.

Important fields: `Type=Application`, `Exec=unison-gui`, `Name=Unison`, `GenericName=File Synchronizer`, `Comment=GUI for Unison file synchronizer`, `Terminal=false`, `Icon=unison-gui`, `StartupNotify=true`, and `Categories=Utility`.

Control flow: no executable code; desktop shells parse the file to display and launch the GUI.

State/persistence: installed as packaging/desktop metadata. It does not alter runtime state except by launching `unison-gui`.

Dependencies/integration: depends on installed `unison-gui` binary and matching icon theme resource.

Risks: packaging must ensure the executable and icon names match installed paths. If distributions rename binaries, this file must be patched.

Test signals: desktop-file validation and manual launcher test are sufficient; CI packaging may indirectly include it.
