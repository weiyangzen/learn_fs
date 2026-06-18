<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c

## Purpose
Decodes and prints a `powerpc` ptrace/core-file register set.

## Important APIs, Types, and Functions
- `arch_decode_fpregset`, `arch_decode_prstatus_regset`, `arch_decode_pt_regs`, or `decode_pt_regs64` reads a tracee memory blob and prints structured fields.
- The decoders use `umove_or_printaddr`, `umoven_or_printaddr`, `PRINT_FIELD_X`, `PRINT_FIELD_ARRAY`, `PRINT_FIELD_ARRAY_UPTO`, and `tprint_more_data_follows`.

## Control Flow
- Compute `fetch_size = MIN(sizeof(regs), size)`, reject zero or misaligned sizes by printing the address, fetch available bytes, then print fields whose offsets are present.
- When the kernel reports more bytes than the known struct, the decoder emits a more-data marker instead of assuming layout.

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
Reviewed the complete local source file `sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c`: 91 lines; 2460 bytes; defines `# define TRACEE_KLONGSIZE 4`, `# define TRACEE_KLONGSIZE SIZEOF_KERNEL_LONG_T`, `#undef TRACEE_KLONGSIZE`; functions `arch_decode_prstatus_regset`. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc/arch_prstatus_regset.c -->
