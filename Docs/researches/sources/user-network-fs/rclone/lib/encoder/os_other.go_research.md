# sources/user-network-fs/rclone/lib/encoder/os_other.go

Source read signal: reviewed complete local file (6 lines, sha256 b7ce6c47b479484e).

Purpose: Selects the local backend filename encoding for non-Windows, non-macOS platforms.

Important APIs/types/functions: Defines build-tagged constant `OS = Base`.

Control flow: No runtime flow; build constraints select this file for Unix-like platforms other than Darwin.

State and persistence behavior: No state. `Base` encodes zero, slash, and dot policy as defined by `standard.go`.

Dependencies and integration points: Integrates with local filesystem path handling and cache DB naming through the shared `encoder.OS` constant.

Risks and test signals: Platform build tags must exclude Windows and Darwin correctly. Behavior assumes other platforms can carry invalid UTF-8 without the Darwin/Windows escaping policy.
