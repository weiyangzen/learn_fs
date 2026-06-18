# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/systm.h

## Purpose
Defines broad kernel system interfaces: global kernel state variables, boot/startup hooks, time-of-day status, timeout/callout APIs, copyin/copyout and low-level memory/string helpers, fault handling, SPL/softcall interfaces, syscall table structures, syscall return values, and kernel/boot string/memory prototypes.

## Main Interfaces
- Kernel globals for clock rate, root/devices vnodes, memory counters, root device/vnode, panic state, scheduler wake flags, kernel text/data bounds, auditing, load averages, ISA list, stack execution policy, NFS zone policy, `maxusers`, and `pidmax`.
- Startup/platform hooks:
  - `startup()`, `clkstart()`, `post_startup()`, `kern_setup1()`, `ka_init()`, `nodename_set()`
- TOD fault support:
  - `enum tod_fault_type`
  - `TOD_*` status flags
  - `tod_validate()`, `tod_status_set()`, `tod_status_clear()`, `plat_tod_fault()`
- Timers/callouts:
  - `timeout()`, `realtime_timeout()`, `untimeout()`
  - generic/default callout APIs and `delay*()` helpers
- Device and conversion helpers:
  - `getudev()`, `cmpldev()`, `expldev()`, `stoi()`, `numtos()`, suboption helpers
- User/kernel copying and fault helpers:
  - `copyin()`, `copyout()`, `copyinstr()`, `copyoutstr()`, `xcopy*()`, `fuword*()`, `suword*()`, no-error variants
  - `on_fault()`, `no_fault()`, `setjmp()`, `longjmp()`
- Memory/string primitives for kernel/boot:
  - `bcopy()`, `bzero()`, `memset()`, `memcpy()`, `memcmp()`, `strlcpy()`, `strlen()`, `strcmp()`, and related functions
- Interrupt/SPL and softcall:
  - `spl*()` functions, `splx()`, `softcall_init()`, `softcall()`, `softint()`
- System call dispatch:
  - `struct sysent`
  - `sysent[]`, `sysent32[]`, `nosys_ent`
  - `NSYSCALL`, syscall flag constants, `rval_t`
  - syscall argument and dispatch helpers
- Overflow helper inline functions for `uint16_t`, `hrtime_t`, and `off_t`.

## Dependencies And Relationships
Pulls different dependencies for standalone vs kernel builds. It is one of the central kernel headers and is used by syscall, VM, device, scheduler, boot, and low-level utility code.

## Research Notes
Several comments define compatibility requirements, especially for `struct sysent`: expansion should only occur at the end, flags must not be reused, and size is performance-sensitive.
