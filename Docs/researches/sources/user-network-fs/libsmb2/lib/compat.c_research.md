# sources/user-network-fs/libsmb2/lib/compat.c

Purpose: Provides platform fallback implementations for functions and socket helpers missing on console, embedded, Windows/Xbox, Amiga, Android, and other non-POSIX targets.

Important APIs/functions: Conditional implementations include `smb2_getaddrinfo`, `smb2_freeaddrinfo`, `random`, `srandom`, `getpid`, `getlogin_r`, `writev`, `readv`, `poll`, `strdup`, `be64toh`, and platform-specific helpers like PS2 `iop_connect`.

Control flow: Almost every function is compiled only when a `NEED_*` or platform macro is defined. Fallback `getaddrinfo` builds a minimal IPv4 `addrinfo`; vectored I/O implementations flatten/scatter buffers through a temporary allocation; fallback `poll` maps requested events onto `select`.

State/persistence: Mostly stateless, except PS2 IOP pseudo-random state `next` and some platform-global errno substitutions. Allocated `addrinfo` and temporary buffers are owned/freed by callers or the function itself.

Dependencies/integration: Paired with `compat.h`, which maps system calls and typedefs per platform. Core libsmb2 networking and file I/O include this layer to build on unusual targets.

Risks: Some fallbacks are deliberately minimal: `smb2_getaddrinfo` lacks full DNS/service/family behavior on many targets, `writev`/`readv` allocate one contiguous buffer and can fail for large vectors, PS2 `asprintf` uses a fixed 256-byte buffer and suspicious `sprintf(str, fmt, args)` varargs handling, and fallback `poll` approximates errors as `POLLHUP`. `be64toh` takes signed `long long` and uses `ntohl` on shifted pieces, so type assumptions matter.

Test signals: Platform build smoke tests are essential. Host-side tests can force `NEED_READV`, `NEED_WRITEV`, `NEED_POLL`, and `NEED_STRDUP` to validate overflow checks, short reads, event mapping, and allocation failures.
