# sources/user-network-fs/rclone/lib/encoder/os_darwin.go

Source read signal: reviewed complete local file (9 lines, sha256 fc31921f690fc33d).

Purpose: Selects the local backend filename encoding for macOS builds.

Important APIs/types/functions: Defines build-tagged constant `OS = Base | EncodeInvalidUtf8`.

Control flow: There is no runtime flow; the Go build selects this file on Darwin and consumers use `encoder.OS` as the platform policy.

State and persistence behavior: No state. The constant affects how local paths are encoded before reaching macOS filesystems.

Dependencies and integration points: Depends on constants from the encoder package. It integrates with local backend path normalization and `kv.makeName` through `encoder.OS.FromStandardPath`.

Risks and test signals: The macOS-specific concern is invalid UTF-8 preservation because macOS cannot store arbitrary invalid UTF-8 names. Cross-platform tests should assert `OS` includes `EncodeInvalidUtf8` only where needed.
