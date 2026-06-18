# File Research: sources/os/bsd/freebsd-src/sys/sys/systm.h

## Scope

This broad kernel header declares many core FreeBSD kernel globals, boot/tuning state, low-level utility APIs, formatted output routines, memory/string primitives, user/kernel copy helpers, clock/profiling hooks, kernel environment helpers, sleep/wakeup APIs, unit-number allocation APIs, and deprecation diagnostics.

## APIs And Constants

- Declares boot and system globals: `cold`, `suspend_blocked`, `rebooting`, `version`, `compiler_version`, `copyright`, `kstack_pages`, `pagesizes`, `physmem`, `realmem`, `rootdevnames`, `boothowto`, `bootverbose`, `maxusers`, `ngroups_max`, `vm_guest`, and `maxphys`.
- Defines `enum VM_GUEST` values for recognized hypervisor/guest environments.
- Defines alignment/placement attributes `__read_mostly`, `__read_frequently`, and `__exclusive_cache_line`.
- Declares hash table helpers, CPU/cache/init routines, LinuxKPI current-state allocation hooks, critical-section entry/exit helpers, early printf hooks, and kernel printf/logging APIs.
- Declares memory/string functions and maps `bcopy`, `bzero`, `bcmp`, `memset`, `memcpy`, `memmove`, and `memcmp` to compiler builtins or sanitizer interceptors.
- Declares early memory functions, `copystr`, `copyin`, `copyinstr`, `copyout`, nofault variants, fetch/store user-word helpers, and compare-and-swap user helpers.
- Declares clock, profiling, eventtimer, kernel environment, cputicker, console/init/reboot/shutdown, sleep/wakeup, cdev naming, delay, root mount holdback, unit-number allocation, interrupt profiling, safe kernel memory read, and obsolete-code warning APIs.
- Provides no-op legacy `spl*()` interrupt-priority stubs.

## Control Flow And Behavior

- `critical_enter()` and `critical_exit()` use inline fast paths unless KBI/module/tracing constraints require function calls; the inline path increments/decrements `td_critnest`, uses interrupt fences, and invokes preemption handling when owed.
- `copystr` is a statement-expression wrapper over `strlcpy()` that returns `ENAMETOOLONG` when the destination buffer is too small and optionally reports copied length.
- Sleep macros translate tick-based timeouts to `sbintime_t` and call `_sleep()` or spin-sleep variants.
- `pause()` wraps `pause_sbt()` with hardclock timing, while `pause_sig()` adds `C_CATCH`.
- Root mount hold tokens allow subsystems to delay root mount completion until required devices or services are ready.
- `gone_in()` and `gone_in_dev()` emit a deprecation warning only once per call site, and can become compile-time assertions when obsolete code is disabled.

## Dependencies

- Includes core kernel headers for types, callouts, assertions, queues, fixed-width integers, atomics, CPU functions, parameters, per-CPU state, and KPI-lite thread state.
- Relies on machine-specific atomic/cpufunc/user-access implementations for many declared primitives.
- Used pervasively by kernel subsystems, including VFS, device drivers, networking, VM, scheduler, console, sysctl/environment, and boot code.

## Risks And Invariants

- This is a high-fanout kernel header; changes can affect almost every kernel translation unit.
- Critical-section accounting must stay balanced or preemption/interrupt invariants break.
- User-copy helpers are security boundaries; callers must check annotated results and respect nofault semantics.
- Sanitizer interception macros must not recurse into sanitizer runtimes incorrectly.
- `gone_in()` uses `__LINE__` to build per-call-site statics; moving or macro-wrapping call sites can change warning identity.
