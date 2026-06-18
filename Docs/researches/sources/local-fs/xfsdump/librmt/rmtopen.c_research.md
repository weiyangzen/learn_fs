# File Research: sources/local-fs/xfsdump/librmt/rmtopen.c

Implements `rmtopen(path, oflag, mode)` and the remote connection setup.

Core behavior:
- Local paths without `:` call `open(2)`.
- Paths with `:` are parsed as remote paths and opened through `rsh` plus remote `/etc/rmt`.
- Remote descriptor returned to caller is internal unit index OR’d with `REM_BIAS`.
- Finds a free slot in the fixed `MAXUNIT` pipe arrays.
- Parses path form with optional user and host.
- Uses `RSH` and `RMT` environment variables to override default remote programs.
- Detects remote host type by running remote `uname` via `popen`.
- Forks an `rsh` child with pipes connected to stdin/stdout.
- Sends `O<device>\n<oflag>\n` and requires successful remote status.

Security/robustness notes:
- Uses legacy `rsh`, not ssh.
- Remote host detection command is built as a shell string for `popen`.
- Fixed-size buffers constrain host/device/login fields.
- `rmtopen()` treats any colon in the path as remote, broader than `_rmt_dev()`.
