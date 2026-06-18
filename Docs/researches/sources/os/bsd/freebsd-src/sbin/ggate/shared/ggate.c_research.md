# File Research: sources/os/bsd/freebsd-src/sbin/ggate/shared/ggate.c

`ggate.c` contains shared support for `ggatec`, `ggated`, and `ggatel`.

Key behavior:
- Provides logging wrappers that write to stdout in verbose mode or syslog otherwise.
- Provides fatal logging helpers that exit after reporting an error.
- Determines media size and sector size for character devices via disk ioctls, and for regular files via `stat`.
- Opens, closes, and performs ioctls on `/dev/<G_GATE_CTL_NAME>`.
- Destroys GEOM Gate units and loads `geom_gate` if the kernel module is absent.
- Provides robust send/receive wrappers:
  - `g_gate_send()` loops until all data is sent or an error occurs and optionally chunks sends by `MAX_SEND_SIZE`.
  - `g_gate_recv()` retries `EAGAIN`.
- Applies TCP/socket settings: `TCP_NODELAY` depending on global `nagle`, `SO_REUSEADDR`, receive/send buffers, and 8-second send/receive timeouts.
- When `LIBGEOM` is defined, implements provider listing by walking the libgeom tree and printing brief or verbose provider metadata.
- Resolves numeric IPv4 addresses or hostnames with `inet_addr()` and `gethostbyname()`.

Important details:
- Default `nagle` value is 1, but the code sets `TCP_NODELAY` when `nagle` is true; `-n` clears it.
- `MAX_SEND_SIZE` defaults to `MAXPHYS`, but comments describe a `ggatec` build-time workaround for large send performance.
- The libgeom listing path prints provider name, info, access, timeout, queue counts, references, media size, sector size, and mode.
