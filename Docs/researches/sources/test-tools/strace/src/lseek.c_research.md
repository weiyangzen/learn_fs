<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/lseek.c -->
# sources/test-tools/strace/src/lseek.c

Purpose: decodes `lseek` and legacy `llseek` offset arguments.
Important APIs/types/functions: `SYS_FUNC(lseek)`, `SYS_FUNC(llseek)`, `current_klongsize`, `printnum_int64`, and `whence_codes`.
Control flow: `lseek` sign-extends offsets when kernel long is narrower; `llseek` combines high/low 32-bit words on entry and prints the result pointer plus whence on exit.
State and persistence behavior: no persistent state. Dependencies and integration points: file-position syscall table entries.
Risks: x32 and other mixed long-size ABIs require exact sign/width handling. Test signals: x32 lseek tests, negative offsets, large 64-bit llseek offsets, and failed result-pointer reads.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/lseek.c -->
