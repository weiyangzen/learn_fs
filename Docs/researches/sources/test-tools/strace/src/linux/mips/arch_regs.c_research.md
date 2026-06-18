<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_regs.c -->
# sources/test-tools/strace/src/linux/mips/arch_regs.c

## Purpose
Declares the cached register snapshot and PC/SP access macros for the strace `mips` backend.

## Important APIs, Types, and Functions
- mips_regs.uregs with v0 at index 2, a0 at index 4, a3 at index 7, stack at index 29, and PC at index 34
- Macros such as `ARCH_REGS_FOR_GETREGS`, `ARCH_REGS_FOR_GETREGSET`, `ARCH_PC_REG`, `ARCH_SP_REG`, or ptrace peek offsets connect generic register-fetch helpers to the architecture layout.

## Control Flow
- No functions are defined; generic `get_regs`, `set_regs`, and stack/PC helpers use these declarations and macros.
- Register state is refreshed from ptrace before syscall decoding and is later consumed by get/set error, syscall-number, and argument helpers.

## State and Persistence Behavior
- The static register object is process-local tracer state reused across decode steps for one traced stop.
- Persistent trace bookkeeping is stored in `struct tcb`; this file only provides the current architecture register snapshot storage or offsets.

## Dependencies and Integration Points
- Integrated with common Linux register helpers and all sibling files that read the architecture register object.
- Depends on kernel UAPI register structs or ptrace offset constants matching the target ABI.

## Risks and Edge Cases
- Incorrect PC/SP mapping breaks stack unwinding, signal-frame decoding, and syscall restart handling.
- Static register layout must match the ptrace request used by the architecture (`GETREGS`, `GETREGSET`, or `PTRACE_PEEKUSER`).

## Test Signals
- Exercise `-i` instruction-pointer output and stack-pointer-dependent decoders on the target architecture.
- Run syscall-entry/exit traces around signal delivery to ensure cached registers are refreshed at the right stops.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/arch_regs.c`: 28 lines; 799 bytes; defines `#define REG_V0 2`, `#define REG_A0 4`, `#define mips_REG_V0 mips_regs.uregs[REG_V0]`, `#define mips_REG_A0 mips_regs.uregs[REG_A0 + 0]`, `#define mips_REG_A1 mips_regs.uregs[REG_A0 + 1]`, `#define mips_REG_A2 mips_regs.uregs[REG_A0 + 2]`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/arch_regs.c -->
