<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_defs_.h -->
# sources/test-tools/strace/src/linux/x86_64/arch_defs_.h

Purpose: declares x86_64 architecture capabilities and personality metadata.
Important APIs/types/functions: defines `SUPPORTED_PERSONALITIES` as three lanes, names/designators for 64/i386/x32, audit-arch pairs, `__X32_SYSCALL_BIT`, old mmap/select and UID16 support, and x32 msqid sizing.
Control flow: no runtime flow; included by common arch setup to size tables and select behavior. State and persistence behavior: compile-time constants only.
Dependencies and integration points: used by syscall table loading, audit-arch matching, personality printing, and compatibility syscall code. Risks: incorrect personality order breaks table indexing across many files. Test signals: startup arch probes and mixed-personality traces should report 64 bit, 32 bit, and x32 accurately.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/x86_64/arch_defs_.h -->
