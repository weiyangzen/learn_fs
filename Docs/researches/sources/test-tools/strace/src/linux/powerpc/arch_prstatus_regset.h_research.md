<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h

## Purpose
Declares the `powerpc` regset structure type consumed by architecture regset decoders.

## Important APIs, Types, and Functions
- The header aliases a kernel UAPI structure or defines a compact local struct such as `struct_fpregset`, `struct_prstatus_regset`, or `struct_pt_regs64`.
- Include guards prevent duplicate type declarations across multi-personality builds.

## Control Flow
- No executable control flow; decoder C files include this type definition and use `offsetof`/`sizeof` against it.

## State and Persistence Behavior
- No persistent state is stored; C decoder files read tracee memory and print output for the current decode call.
- Header files define compile-time layout contracts only.

## Dependencies and Integration Points
- Integrated by ptrace `PTRACE_GETREGSET` and core-note decoding paths.
- Depends on kernel UAPI register structs and strace print helpers.

## Risks and Edge Cases
- Alignment checks and `offsetof` thresholds must match kernel layouts for 32-bit, 64-bit, and compat personalities.
- A too-small or too-large size must be handled without reading past available tracee memory.

## Test Signals
- Decode NT_PRSTATUS and FP regset notes from target-architecture core files.
- Test short, exact-size, and oversized regset blobs to exercise conditional field printing.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h`: 15 lines; 334 bytes; defines `# define STRACE_ARCH_PRSTATUS_REGSET_H`, `# define HAVE_ARCH_PRSTATUS_REGSET 1`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.h -->
