# sources/test-tools/strace/src/linux/x32/shuffle_scno.c

## Purpose
Defines x32 syscall-number shuffling between strace's internal/personality representation and the kernel-visible x32 syscall encoding.

## Important APIs, Types, And Functions
Exports `kernel_ulong_t shuffle_scno_pers(kernel_ulong_t scno, int pers)`. For native x32 personality (`pers == 0`) and a valid syscall number (`scno != (kernel_ulong_t) -1`), it toggles `__X32_SYSCALL_BIT` with XOR. For all other personalities, including the sentinel `-1`, it returns the number unchanged.

## Control Flow
Control flow is a single conditional branch. If native x32 and not the invalid syscall sentinel, toggle the bit; return the resulting syscall number. This symmetric XOR design means the same helper can convert in either direction between internal and kernel-numbered forms.

## State And Persistence
The function is pure: no global state, no mutation, no I/O, and no persistence. Its only state dependency is the caller-provided personality value and the compile-time `__X32_SYSCALL_BIT` constant.

## Dependencies And Integration Points
Depends on `kernel_ulong_t` and `__X32_SYSCALL_BIT`. Integrated through `defs.h` as `shuffle_scno_pers` and the current-personality shorthand. Call sites include syscall-name lookup and basic syscall filters. It works alongside x32 `check_scno.c`, x86_64 personality detection, and `set_scno.c`, all of which need consistent treatment of the x32 marker bit.

## Risks
The helper intentionally preserves `-1`; losing that guard would turn the invalid sentinel into a plausible-looking syscall number. Personality numbering is also critical: only `pers == 0` is treated as x32-native in this directory. Incorrect use before/after `set_scno` can double-toggle or fail to toggle `__X32_SYSCALL_BIT`, causing filters or injection to match the wrong syscall.

## Test Signals
Unit-level checks can assert that native x32 syscall numbers toggle `0x40000000` and toggle back when applied twice, while i386/other personalities remain unchanged. Integration tests should cover syscall name lookup, `-e trace=` filters, and syscall substitution for x32-native calls.

## Source-Read Signal
Reviewed the complete local file and integration references in `basic_filters.c`, `syscall_name.c`, `defs.h`, x32 `check_scno.c`, and x86_64 personality logic.
