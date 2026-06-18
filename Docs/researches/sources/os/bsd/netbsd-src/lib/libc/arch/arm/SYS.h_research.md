# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/SYS.h

This header defines ARM syscall stub macros. It emits `svc` directly in ARM mode and uses a Thumb `emitsvc` macro to place syscall numbers into `r0` before `svc #255`; common macros build no-error, normal, raw, and weak syscall wrappers. Error paths branch to hidden `__cerror`, with special Thumb-1 handling that calls through a saved link register.
