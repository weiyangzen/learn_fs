# sources/user-network-fs/rclone/fs/config/config_read_password_unsupported.go

Purpose: provides a Plan 9 fallback for password input where `golang.org/x/term` support is unavailable.

Important APIs/functions: `ReadPassword() string`, built under `plan9`.

Control flow: simply delegates to `ReadLine("")`, meaning input is read as a normal line.

State and persistence behavior: no persistence; reads from stdin through the shared UI line reader.

Dependencies and integration points: keeps the config password API available on unsupported terminal platforms.

Risks: password entry is echoed on this platform fallback. This is explicitly documented in the file comments.

Test signals: no direct test in this subset.
