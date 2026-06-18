# sources/user-network-fs/rclone/lib/encoder/os_windows.go

Source read signal: reviewed complete local file (33 lines, sha256 75f62dadc543d117).

Purpose: Selects the local backend filename encoding for Windows builds, reflecting Windows reserved character and trailing-name rules.

Important APIs/types/functions: Defines `OS = Base | EncodeWin | EncodeBackSlash | EncodeCtl | EncodeRightSpace | EncodeRightPeriod | EncodeInvalidUtf8`.

Control flow: No runtime flow; consumers use the constant for platform-specific path conversion.

State and persistence behavior: No state. The constant controls persistent local filenames and must remain compatible with existing encoded paths.

Dependencies and integration points: Depends on encoder flag constants and documents Windows character substitutions and invalid UTF-8 handling before UTF-16 conversion.

Risks and test signals: Omitting a reserved Windows rule can cause create/open failures or name collisions. Tests should verify trailing spaces/periods, control characters, backslash, and invalid UTF-8 behavior on Windows builds.
