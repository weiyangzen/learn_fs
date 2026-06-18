<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/syscallent.h -->
# sources/test-tools/strace/src/linux/xtensa/syscallent.h

Purpose: Xtensa syscall dispatch table.
Important APIs/types/functions: `sysent` rows with argument counts, flags, `SEN` decoder symbols, includes `../32/syscallent-common-32.h` and `syscallent-common.h`.
Control flow: declarative table indexed by `tcp->scno` after `get_scno`. State and persistence behavior: static build-time data.
Dependencies and integration points: Xtensa syscall decoding, filtering, and classification. Risks: wrong numbers/flags produce incorrect output and filtering. Test signals: generated syscall-table checks and Xtensa syscall trace fixtures including architecture-specific early entries `spill` and `xtensa`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/xtensa/syscallent.h -->
