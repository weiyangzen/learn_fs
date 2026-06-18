# sources/test-tools/strace/src/fetch_struct_iovec.c

Mpers fetch helper for `struct iovec`. It copies tracee `iov_base` and `iov_len` into the project `iovec` abstraction used by vector IO decoders. State is limited to the destination object. Dependencies are `<sys/uio.h>`, `MPERS_DEFS`, and `iovec.h`. Risks are pointer width conversion and length truncation when tracing compat processes. Tests should cover readv/writev and socket message paths under native and compat personalities, including inaccessible iovec pointers.
