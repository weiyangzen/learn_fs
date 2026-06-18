<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/arch_defs_.h -->
# sources/test-tools/strace/src/linux/or1k/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `or1k` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to AUDIT_ARCH_OPENRISC.
- Feature macros such as `HAVE_ARCH_OLD_MMAP`, `HAVE_ARCH_OLD_SELECT`, `HAVE_ARCH_UID16_SYSCALLS`, `HAVE_ARCH_GETRVAL2`, `HAVE_ARCH_DEDICATED_ERR_REG`, and `CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL` enable or disable shared backend code paths when present.

## Control Flow
- There is no executable control flow; this header is included during architecture backend compilation.
- The macro set selects legacy syscall aliases, compat handling, dedicated errno-register behavior, and audit architecture tagging before any tracee is run.

## State and Persistence Behavior
- Pure build-time state. It does not allocate runtime storage, but it changes how `struct tcb` fields are interpreted by the compiled backend.

## Dependencies and Integration Points
- Integrated by common strace Linux backend headers and syscall-personality setup.
- Depends on Linux audit constants, ELF machine constants for older ports, and sibling syscall-base headers where included.

## Risks and Edge Cases
- A wrong capability macro usually compiles cleanly but selects the wrong shared decoder behavior.
- Compat and audit macros are especially risky because they affect syscall-table selection before individual syscall decoding starts.

## Test Signals
- Run an architecture build for `or1k` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/or1k/arch_defs_.h`: 1 lines; 59 bytes; defines `#define PERSONALITY0_AUDIT_ARCH { AUDIT_ARCH_OPENRISC, 0 }`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/or1k/arch_defs_.h -->
