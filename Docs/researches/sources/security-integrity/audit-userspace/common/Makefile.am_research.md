<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/Makefile.am -->
# sources/security-integrity/audit-userspace/common/Makefile.am

Purpose: automake file for the internal common utility library.

Important build API: builds noinst `libaucommon.la` from `strsplit.c`, `common.c`, and `message.c`; declares `common.h`; sets PIC/GNU source/debug CFLAGS and include paths for project root and lib.

Control flow and state: no runtime logic; automake compiles utilities for internal linkage.

Dependencies and integration: `common.h` exposes hidden symbols and atomics used by auditd, audisp, auplugin, and related components.

Risks and test signals: because the library is internal and shared by privileged daemons, small utility regressions can have broad blast radius. Build success and downstream tests are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/common/Makefile.am -->
