<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/asm_stat.h -->
# sources/test-tools/strace/src/linux/x86_64/asm_stat.h

Purpose: supplies a corrected x32 `struct stat` view while otherwise using generic stat definitions.
Important APIs/types/functions: include guard, temporary `stat` redirection for x32 ILP32, generic `asm_stat.h`, and replacement `struct stat` with kernel-sized fields.
Control flow: preprocessor-only selection. State and persistence behavior: type declarations only.
Dependencies and integration points: stat-family syscall decoders and x32 builds with older kernel headers. Risks: wrong x32 stat layout corrupts file metadata output. Test signals: x32 stat/lstat/fstat output tests with large inode and timestamp values.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/asm_stat.h -->
