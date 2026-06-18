# File Research: sources/local-fs/udftools/libudffs/misc.c

Shared utility functions for udftools.

Defines global `const char *appname` used by error reporting.

Functions:
- `gen_uuid_from_vol_set_ident`: decodes the UDF Volume Set Identifier and derives a 16-byte text UUID-like value from its first characters, with fallback byte-hex encoding when non-hex characters appear.
- `strtou32`: strict unsigned 32-bit parser using signed `strtoll` to catch underflow and leading whitespace.
- `strtou16`: strict unsigned 16-bit parser layered on `strtou32`.
- `randu32`: reads from `/dev/urandom` when possible, otherwise seeds and combines libc `rand`.
- `read_nointr`: retries `read` on `EINTR`.
- `write_nointr`: retries `write` on `EINTR`.

Notable behavior:
- The I/O wrappers retry only interrupted calls; they do not loop to satisfy a full requested byte count.
- `randu32` is suitable for identifiers, not cryptographic protocol guarantees.
