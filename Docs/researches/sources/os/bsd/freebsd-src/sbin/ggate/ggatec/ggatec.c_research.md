# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/ggatec.c

`ggatec.c` implements the GEOM Gate network client. It supports `create`, `rescue`, `destroy`, and `list`, creating a local `/dev/ggateN` provider backed by a remote `ggated` export.

Key behavior:
- Establishes two TCP connections to the server, paired by a random token: one for client receive/server send and one for client send/server receive.
- Performs a version handshake using `GGATE_MAGIC` and `GGATE_VERSION`, then sends `g_gate_cinit` with path, flags, token, and connection direction.
- Receives remote media size and sector size through `g_gate_sinit`; user-provided sector size overrides server sector size only when set.
- `send_thread()` waits for kernel GEOM requests via `G_GATE_CMD_START`, translates `BIO_READ`, `BIO_WRITE`, and `BIO_FLUSH` into ggate protocol commands, and sends headers/data to the server.
- `recv_thread()` receives server completions, optional read data, and completes kernel requests with `G_GATE_CMD_DONE`.
- Reconnection is coordinated with a global `reconnect` flag and `SIGUSR1` to interrupt the peer thread; `g_gatec_loop()` reconnects and cancels outstanding requests.
- `create` loads/open the GEOM gate control device, creates the provider, daemonizes unless verbose, then enters the reconnect loop.
- `rescue` reconnects to an existing unit and cancels outstanding kernel requests before serving.
- `destroy` and `list` delegate to shared helpers.

Important details:
- Buffer sizing starts from `kern.maxphys` when available, otherwise 128 KiB.
- `-o ro|wo|rw|direct`, `-n`, `-p`, `-q`, `-R`, `-S`, `-s`, `-t`, `-u`, and `-v` are parsed with action-specific validation.
- Network fields are byte-swapped with shared inline helpers from `ggate.h`.
- Error handling generally exits through `g_gate_xlog()` for unrecoverable ioctl/protocol failures.
