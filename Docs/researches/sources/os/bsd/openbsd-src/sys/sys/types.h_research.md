# File Research: sources/os/bsd/openbsd-src/sys/sys/types.h

Central OpenBSD system type header. It defines BSD aliases (`u_char`, `u_int`, etc.) under `__BSD_VISIBLE`, exact-width integer types, BSD `u_int*_t`, deprecated quad types, VM address/size types, and core POSIX/system types such as `dev_t`, `ino_t`, `uid_t`, `gid_t`, `off_t`, `time_t`, `clock_t`, and `pid_t`.

Under BSD userland visibility it declares `lseek`, `ftruncate`, and `truncate` to ensure `off_t` promotion. It also provides `major`, `minor`, and `makedev`. Kernel mode gets common forward declarations and a `bool` definition backed by `_Bool`.
