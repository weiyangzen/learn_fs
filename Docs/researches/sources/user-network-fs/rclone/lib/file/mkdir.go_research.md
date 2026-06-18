# sources/user-network-fs/rclone/lib/file/mkdir.go

Source read signal: reviewed complete local file (8 lines, sha256 db2ca063e2cf2bb9).

Purpose: Keeps a package-level `MkdirAll` wrapper around `os.MkdirAll`.

Important APIs/types/functions: Exports `MkdirAll(path string, perm os.FileMode) error`.

Control flow: Directly delegates to `os.MkdirAll`.

State and persistence behavior: Creates directories persistently according to the filesystem and permissions.

Dependencies and integration points: Uses `os`. The wrapper preserves a stable package API for callers that historically used `lib/file`.

Risks and test signals: Behavior is standard library behavior; tests should live at higher-level callers that depend on directory creation.
