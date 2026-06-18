# File Research: sources/local-fs/xfsdump/inventory/inv_core.c

Provides low-level inventory disk I/O helpers over fixed-size on-disk records.

Key functions:
- `get_counters()` reads a counter block at offset zero, validates `INV_VERSION`, and returns `ic_curnum`.
- `get_headers()` allocates and reads a header/entry array from a supplied offset.
- `get_invtrecord()` and `put_invtrecord()` wrap `pread()`/`pwrite()` with optional `flock()` locking.
- `get_headerinfo()` reads counters and, if nonempty, the corresponding header array.
- `get_lastheader()` reads counters plus all headers and copies the last one to a caller-owned allocation.

Important dependencies:
- Used through macros in `inv_priv.h`: `GET_REC`, `GET_REC_NOLOCK`, `GET_ALLHDRS_N_CNTS`, `PUT_REC`, `GET_COUNTERS`, and related helpers.
- Relies on callers to choose locking correctly. Several higher layers call `_NOLOCK` variants only while already holding a lock.

Notable observations:
- Short reads/writes are treated as errors.
- Version mismatch logs and asserts, so unsupported inventory versions are fatal in debug/assert-enabled builds.
- `get_lastheader()` returns the number of headers as well as the copied header, which callers use as a one-based index.
