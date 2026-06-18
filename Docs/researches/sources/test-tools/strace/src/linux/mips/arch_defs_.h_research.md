<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_defs_.h -->
# sources/test-tools/strace/src/linux/mips/arch_defs_.h

## Purpose
Declares compile-time architecture capability macros for the strace Linux `mips` backend.

## Important APIs, Types, and Functions
- `PERSONALITY0_AUDIT_ARCH` maps the personality to MIPS o32/n32/n64 audit personalities selected by ABI/endian macros.
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
- Run an architecture build for `mips` and verify the generated personality table.
- Trace legacy mmap/select/UID16 or compat syscalls when the corresponding macro is enabled.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_defs_.h`: 28 lines; 851 bytes; defines `#define HAVE_ARCH_GETRVAL2 1`, `#define HAVE_ARCH_DEDICATED_ERR_REG 1`, `#define CAN_ARCH_BE_COMPAT_ON_64BIT_KERNEL 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_defs_.h -->
