# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_clamav.c

## Purpose
This file implements the ClamAV `clamd` backend for `vfs_virusfilter`. It translates Samba file scan requests into ClamAV `zSCAN` commands over a Unix-domain socket and maps clamd replies into `virusfilter_result` values.

## Important APIs, Types, and Functions
`virusfilter_clamav_init()` sets the default socket path, allocates `struct virusfilter_backend`, names it `clamav`, and installs `virusfilter_backend_clamav`. `virusfilter_clamav_connect()` configures NUL-terminated read/write lines for clamd z-commands. `virusfilter_clamav_scan_init()` connects to `config->socket_path` as root through the shared I/O helper. `virusfilter_clamav_scan()` sends `zSCAN <cwd>/<fname>`, parses `<FILEPATH>: <REPORT> <TOKEN>`, and returns clean, infected, or error. `virusfilter_clamav_scan_end()` disconnects.

## Control Flow
The core module calls backend connect once during VFS connect to configure EOL behavior. For each scan, `scan_init` opens the socket, `scan` sends one command and reads one response, and `scan_end` closes the stream unless the core request-limit logic keeps it alive. Reply validation checks the filepath prefix separator, finds the last space-delimited token, and handles `OK`, `FOUND`, and `ERROR`.

## State and Persistence
The backend stores no private state beyond the shared `config->io_h` stream and `config->socket_path`. It defaults to `/var/run/clamav/clamd.ctl` unless a build-time macro or smb.conf value overrides it. Scan reports are talloc strings returned to the core.

## Dependencies and Integration Points
It depends on `vfs_virusfilter_common.h` for the backend contract and on `vfs_virusfilter_utils.h` for socket line I/O. It integrates with clamd's local socket protocol and the core's cache/remediation policy.

## Risks
The parser assumes clamd echoes exactly the path length formed from `cwd_fname/fname`; path encoding or unusual names could make validation fail. The code indexes `reply[filepath_len + 1]` after receiving arbitrary scanner output, so malformed short replies rely on surrounding memory safety assumptions. Scanning uses filesystem paths visible to clamd, so permissions and chroot/container layout must match smbd's view.

## Test Signals
Mock clamd replies for `OK`, `FOUND`, `ERROR`, malformed missing colon, missing final token, short replies, socket connect failure, and NUL EOL behavior. Integration tests should confirm default and configured socket paths.
