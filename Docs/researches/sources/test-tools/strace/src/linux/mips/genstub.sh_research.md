<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/genstub.sh -->
# sources/test-tools/strace/src/linux/mips/genstub.sh

## Purpose
Generates placeholder MIPS syscall-table rows for unsupported or compatibility syscall ranges.

## Important APIs, Types, and Functions
- The shell script emits bracketed syscall table rows that map a numeric range to `SEN(printargs)` with generated `syscall_<nr>` names.
- It is a maintenance tool for table generation, not a runtime strace component.

## Control Flow
- The script iterates over numeric arguments/ranges supplied by the maintainer and prints C initializer rows.
- Generated rows can then be pasted or redirected into syscall table headers.

## State and Persistence Behavior
- No runtime tracer state; output is generated text that may become source-table state if checked in.

## Dependencies and Integration Points
- Used by maintainers alongside MIPS syscall table headers.
- Depends on POSIX shell arithmetic and the table macro format expected by strace.

## Risks and Edge Cases
- Generated placeholders are intentionally low-information; leaving them in active ranges means strace will print raw arguments instead of semantic decoders.
- Range mistakes can overwrite real syscall metadata.

## Test Signals
- Run the script on small sample ranges and diff output against expected C initializer syntax.
- After using generated rows, build strace and trace a syscall in the affected range.

## Source-Read Signal
Reviewed the complete local source file `sources/test-tools/strace/src/linux/mips/genstub.sh`: 15 lines; 434 bytes; 1 `SEN(...)` syscall decoder references; first printargs; last printargs. This report is derived from the full file plus adjacent strace architecture integration conventions visible in the same source tree.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/mips/genstub.sh -->
