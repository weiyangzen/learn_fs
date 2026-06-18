# File Research: sources/os/plan9/plan9/sys/src/9/pc/initcode.s

- Size/hash: 23 lines, 282 bytes, SHA-256 `5aad3ae5db916f7ab353b139cfe140ab830073c6fe3436a51650de505750914f`.
- Purpose: First user text copied by `main.c:userinit` into the initial process. It immediately executes `/boot`.
- Contents: Includes syscall numbers, defines `TEXT main(SB)`, builds arguments for `exec("/boot", bootv)`, invokes Plan 9 syscall trap `INT $64` with `EXEC`, then loops forever if exec returns.
- Data: Defines global `boot` string storage containing `"/boot"`.
- Integration: `main.c` copies `initcode` into the first user text page and builds the user stack with boot arguments; this assembly is the first user-mode instruction sequence.
- Dependencies: `/sys/src/libc/9syscall/sys.h`, kernel syscall vector `VectorSYSCALL = 64`.
- Research notes: Bootstraps the user-level root of the system. Filesystem relevance is early: `/boot` resolution begins the user-space boot and namespace setup path.
