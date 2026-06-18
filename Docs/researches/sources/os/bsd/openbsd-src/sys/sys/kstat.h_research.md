# File Research: sources/os/bsd/openbsd-src/sys/sys/kstat.h

This header defines the OpenBSD kstat ioctl ABI, named value format, and kernel registration interface.

Key definitions:
- String lengths and kstat types: `KSTAT_STRLEN`, `KSTAT_T_RAW`, `KSTAT_T_KV`, `KSTAT_T_COUNTERS`.
- `struct kstat_req` for ioctl discovery/read metadata and data pointer/length.
- Ioctls: version and find/next-find by id/provider/name.
- Named value constants: `KSTAT_KV_NAMELEN`, `KSTAT_KV_ALIGN`.
- `enum kstat_kv_type` for null, bool, counters, integers, inline/trailing strings/bytes, temperature, frequency, voltage, current, and power.
- `enum kstat_kv_unit`.
- `struct kstat_kv` and access macros.

Kernel definitions:
- `struct kstat` with id, provider/name/unit identity, type/flags/state, timestamps, RB-tree entries, data version, callbacks, lock ops, data pointer/length/update interval.
- APIs: `kstat_create`, lock setters, `kstat_read_nop`, `kstat_install`, `kstat_remove`, `kstat_destroy`, `kstat_kv_init`, `kstat_kv_unit_init`.
- Initializer macros: `KSTAT_KV_INITIALIZER`, `KSTAT_KV_UNIT_INITIALIZER`.

Risk notes:
- `struct kstat_req` contains a user data pointer and datalen; ioctl handlers must validate copy sizes and versioning.
- `KSTAT_F_REALLOC` and data version fields imply readers must handle data replacement/races.
