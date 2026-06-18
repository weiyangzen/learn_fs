# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/linux.c

Linux sysfs attribute utility implementation.

Key behavior:
- Writes sysfs-like attributes by opening `<dir>/<attr>` for write and writing the provided string.
- Reads attributes by opening `<dir>/<attr>`, reading up to 4095 bytes, trimming one trailing newline and trailing spaces, and returning a duplicated string.
- Exposes helpers for subsystem, controller, namespace, and path objects by using their sysfs directory accessors.

Important dependencies:
- Linux file APIs: `open`, `read`, `write`, `close`.
- `asprintf()` for path construction.
- cleanup helpers for fd/free management.
- libnvme tree sysfs directory accessors.

Research notes:
- `libnvme_set_attr()` returns the raw `write()` result on success, not normalized zero.
- `libnvme_get_attr()` returns `NULL` for open/read failure or empty trimmed value; it resets `errno` to zero after successful reads.
