# sources/test-tools/strace/src/iovec.h

Purpose: defines strace's ABI-sized iovec representation for tracee memory decoding.

Important APIs/types/functions: `strace_iovec`, `kernel_ulong_t`, and the include guard `STRACE_IOVEC_H`.

Control flow: header-only typedef; including code receives a two-field structure with `iov_base` and `iov_len` sized as kernel unsigned longs for the current personality.

State and persistence behavior: no state. The type is used as a stable in-memory layout description for fetched tracee iovec arrays.

Dependencies and integration points: includes `kernel_types.h`; used by decoders such as vector I/O/keyctl helpers that need tracee ABI pointer and length fields rather than host `struct iovec`.

Risks: incorrect `kernel_ulong_t` sizing would corrupt vector decoding across compat personalities. The type intentionally does not include libc's pointer type because host ABI may differ from tracee ABI.

Test signals: iov-based syscall tests should exercise native and compat personalities and confirm base/length pairs are not truncated or widened incorrectly.
