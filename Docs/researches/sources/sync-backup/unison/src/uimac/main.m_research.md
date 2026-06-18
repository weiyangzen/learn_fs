<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/main.m -->
# sources/sync-backup/unison/src/uimac/main.m

Source read: complete file, 53 lines, 1756 bytes, sha256 `ed2009bdfd179533`.

Purpose: Mac UI process entry point. It strips Finder process-serial-number arguments, starts the OCaml bridge/runtime, handles command-line modes that should run without the GUI, and otherwise enters `NSApplicationMain`.

Important APIs/types/functions: `main` calls `[Bridge startup:argv]`, tests arguments such as `-doc`, `-help`, `-version`, `-server`, `-socket`, and `-ui`, and invokes OCaml `unisonNonGuiStartup` through `ocamlCall`.

Control flow: An autorelease pool is created, a Finder `-psn_` argument is removed when present, OCaml starts before AppKit main loop, and each command-line flag that may be non-GUI triggers OCaml startup. If OCaml exits, the process ends; if it returns because GUI mode is needed, AppKit starts normally.

State and persistence behavior: Mutates local `argc/argv` for Finder launches. No persistent state is stored here.

Dependencies and integration points: Depends on Cocoa, `Bridge`, OCaml command-line startup logic, and `NSApplicationMain` loading the main nib.

Risks: Starting OCaml before AppKit main loop means bridge initialization failures abort the app early. The flag loop can call non-GUI startup multiple times if multiple flags are present unless OCaml exits first. `argv` is `const char **` but later cast in the bridge.

Test signals: Launch from Finder, `open`, direct binary execution, `cltool -version`, server/socket modes, and `-ui graphic` fallback to GUI.
<!-- END_FILE_RESEARCH: sources/sync-backup/unison/src/uimac/main.m -->
