# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ontrap.h

## Purpose

`ontrap.h` defines the kernel `on_trap()` / `no_trap()` exception-protection interface and the `on_trap_data_t` stack record. It is not a public DDI interface. It protects selected code regions from machine exceptions by returning through a setjmp-like mechanism.

## Semantics

`on_trap()` returns zero when installed normally and nonzero when returning after a protected exception. Callers must test only zero versus nonzero. `no_trap()` pops the active trap-protection record; callers must invoke it even after an exception return because catching a trap does not modify `t_ontrap`.

Nested calls are supported through a linked list rooted in the current thread's `t_ontrap`. Reusing the same `on_trap_data` address modifies the top stack element in place, allowing loop usage without pushing duplicate records. `no_trap()` is permitted on an empty stack and only changes thread trap state.

Protection bits are `OT_DATA_ACCESS`, `OT_DATA_EC`, and on x86 `OT_SEGMENT_ACCESS`. The header states that unsupported protection types must panic rather than silently continue unprotected.

## Data Structure And Interfaces

`on_trap_data_t` stores active protection bits, actual trap bit, optional trampoline PC, longjmp label buffer, previous record pointer, access handle, and reserved padding. In kernel builds, it declares `on_trap()`, `no_trap()`, and the default `on_trap_trampoline()`.

## Research Notes

This interface is dangerous by design. Audit focus should be balanced `on_trap()`/`no_trap()` pairs, stack lifetime of `on_trap_data_t`, platform support for requested bits, and ensuring protected regions do not leak locks/resources when an exception path longjmps back.
