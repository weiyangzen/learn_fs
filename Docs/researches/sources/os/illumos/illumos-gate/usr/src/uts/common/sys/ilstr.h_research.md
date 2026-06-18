# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ilstr.h

This newer illumos header defines a small growable/preallocated string builder interface usable in kernel and user contexts.

Key definitions:
- Includes kernel or user headers depending on `_KERNEL`.
- `ilstr_errno_t`: OK, no memory, overflow, printf error.
- `ilstr_flag_t`: `ILSTR_FLAG_PREALLOC`.
- `ilstr_t` stores data pointer, allocated length, string length, error state, kernel memory flag, and flags.

API:
- Initialization: `ilstr_init`, `ilstr_init_prealloc`.
- Lifecycle: `ilstr_reset`, `ilstr_fini`.
- Mutators: append/prepend string, append/prepend char, printf append via `ilstr_aprintf` and `ilstr_vaprintf`.
- Accessors: error, C string, length, empty check, error string.

Relevance:
- General utility useful for kernel diagnostics, formatting, generated names/paths, and administrative output.
