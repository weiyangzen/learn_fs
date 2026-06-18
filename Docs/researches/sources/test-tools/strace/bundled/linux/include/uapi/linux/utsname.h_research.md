# sources/test-tools/strace/bundled/linux/include/uapi/linux/utsname.h

Purpose: defines the historical and current Linux UTS name structures returned by uname-related syscalls. The file preserves old ABI layouts while exposing `struct new_utsname` with the domain name field used by modern `uname`.

Important APIs/types/functions: exported constants are `__OLD_UTS_LEN` set to 8 and `__NEW_UTS_LEN` set to 64. Exported types are `struct oldold_utsname`, with five 9-byte character arrays; `struct old_utsname`, with five 65-byte arrays; and `struct new_utsname`, with six 65-byte arrays for `sysname`, `nodename`, `release`, `version`, `machine`, and `domainname`. There are no functions or inline helpers.

Control flow: none in this header. Kernel uname paths fill one of these fixed-size records, and user space reads the resulting character arrays according to the syscall/compat ABI it invoked.

State/persistence behavior: the structs carry snapshots of kernel UTS state at syscall time. The header itself owns no state and has no persistence. The terminating-byte sizing pattern is explicit: usable lengths are 8 or 64 characters plus one byte for NUL termination.

Dependencies/integration: has only an include guard and no type includes. strace and compat layers use these layouts to decode `oldolduname`, `olduname`, and `uname` results and to distinguish whether `domainname` is present.

Risks and test signals: the main risk is confusing payload length with array size, especially `__NEW_UTS_LEN + 1`, or printing `domainname` for old layouts. Tests should cover all three layouts, exact string truncation/termination, and architecture compat paths where older uname syscalls still appear.
