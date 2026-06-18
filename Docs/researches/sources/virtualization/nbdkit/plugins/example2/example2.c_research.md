# File Research: sources/virtualization/nbdkit/plugins/example2/example2.c

POSIX read-only file-serving example plugin.

Key behavior:
- Requires `file=<filename>`, resolved with `nbdkit_realpath`.
- Opens the file per connection with `open(O_RDONLY|O_CLOEXEC)`.
- Stores fd in a per-connection handle.
- Gets size with `fstat`, rejecting block devices for simplicity.
- Reads with a retrying `pread` loop until requested bytes are satisfied.
- Reports extra compile/runtime info via `dump_plugin`.
- Demonstrates custom debug flag `-D example2.extra=1`.

Educational focus:
- Shows config/config_complete, unload, per-connection handles, error reporting, and errno preservation.
