# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/lwp.h

## Role

Lightweight process public definitions for `_lwp_*` interfaces, LWP creation flags, and LWP accounting info.

## Structure

Includes synchronization and ucontext headers, defines LWP creation flags, `struct lwpinfo`, `_SYSCALL32` `struct lwpinfo32`, `lwpid_t`, private FS/GS base selector constants, private get/set constants, and userland `_lwp_*` prototypes.

## Dependencies And Consumers

Userland consumes the `_lwp_*` declarations. Kernel compatibility code uses `lwpinfo32`. The header relies on `timestruc_t`, `timestruc32_t`, and integer typedefs.

## Important Details

`struct lwpinfo` reserves `lwpinfo_pad[64]`, giving the ABI room for expansion. The `_lwp_*` function prototypes are hidden from `_KERNEL` builds.

## Research Notes

Read completely: 90 lines, 1979 bytes.
