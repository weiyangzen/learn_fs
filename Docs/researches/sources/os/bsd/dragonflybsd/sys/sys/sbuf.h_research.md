# File Research: sources/os/bsd/dragonflybsd/sys/sys/sbuf.h

This header defines the `sbuf` string/binary buffer API used for bounded and auto-extending formatted output.

Key responsibilities:
- Defines opaque `struct sbuf` API plus the concrete structure layout:
  - backing buffer
  - optional drain function and argument
  - error, size, length, flags, section length
- Defines drain callback type `sbuf_drain_func`.
- Defines user-selectable flags:
  - `SBUF_FIXEDLEN`
  - `SBUF_AUTOEXTEND`
  - `SBUF_USRFLAGMSK`
- Defines internal flags:
  - `SBUF_DYNAMIC`
  - `SBUF_FINISHED`
  - `SBUF_DYNSTRUCT`
  - `SBUF_INSECTION`
- Declares construction, mutation, formatting, trimming, finishing, access, and deletion APIs.
- Declares section APIs:
  - `sbuf_start_section()`
  - `sbuf_end_section()`
- Declares kernel-only UIO/copyin helpers:
  - `sbuf_uionew()`
  - `sbuf_bcopyin()`
  - `sbuf_copyin()`

Important invariants:
- `sbuf_new_auto()` constructs a dynamically allocated auto-extending sbuf.
- `sbuf_printf()` and `sbuf_vprintf()` carry format-checking attributes.
- The finished state is explicit; callers generally must call `sbuf_finish()` before treating data as finalized.

Research notes:
- This header is a reusable formatting and incremental-output utility, visible to both kernel and user contexts with kernel-only extensions.
