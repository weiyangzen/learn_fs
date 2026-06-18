# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatel/ggatel.c

`ggatel.c` implements a local GEOM Gate provider backed directly by a local file or character device, without the network protocol.

Key behavior:
- Supports `create`, `rescue`, `destroy`, and `list`.
- `create` opens the backing path, creates a GEOM Gate provider with local media size and sector size, then serves requests.
- `rescue` opens the path, cancels outstanding requests for an existing unit, and resumes serving.
- `destroy` and `list` use shared ggate helpers.
- `g_gatel_serve()` daemonizes unless verbose, waits for kernel requests with `G_GATE_CMD_START`, performs local I/O, then completes requests with `G_GATE_CMD_DONE`.
- Handles `BIO_READ` with `pread()` and `BIO_WRITE`/`BIO_DELETE` with `pwrite()`.
- Unsupported commands return `EOPNOTSUPP`.
- Buffer grows on `ENOMEM` from the GEOM ioctl path or on large reads.

Important details:
- Access mode follows `-o ro|wo|rw`; `-o direct` adds direct I/O behavior to local opens.
- `create` opens with `O_DIRECT | O_FSYNC` in addition to the chosen access mode.
- `rescue` uses access flags but not the `O_DIRECT | O_FSYNC` additions used by `create`.
- Sector size and timeout are configurable only on create.
