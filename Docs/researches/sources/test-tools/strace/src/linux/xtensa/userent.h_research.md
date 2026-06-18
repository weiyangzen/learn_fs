<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/userent.h -->
# sources/test-tools/strace/src/linux/xtensa/userent.h

Purpose: Xtensa register-name lookup table.
Important APIs/types/functions: entries for `a0..a15`, `pc`, `syscall_nr`, `ar0..ar63`, loop registers, shift amount, windowbase/windowstart, and processor state.
Control flow: declarative lookup table only. State and persistence behavior: static data.
Dependencies and integration points: register display and ptrace diagnostics. Risks: wrong constants make windowed-register diagnostics misleading. Test signals: register-name output tests for general and special Xtensa registers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/userent.h -->
