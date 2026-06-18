<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/Makefile.am -->
# sources/security-integrity/audit-userspace/auplugin/Makefile.am

Purpose: automake definition for building and installing the `libauplugin` library and descending into its test directory.

Important build API: declares `SUBDIRS = test`, `VERSION_INFO = 1:0`, `lib_LTLIBRARIES = libauplugin.la`, installed header `auplugin.h`, sources `auplugin-fgets.c` and `auplugin.c`, and links against `audisp/libqueue.la`, `auparse/libauparse.la`, and pthread.

Control flow and state: automake uses it to compile PIC code with project warning flags and include paths for top-level, lib, common, auparse, auplugin, audisp, and src.

Dependencies and integration: integrates plugin helper APIs with the audit dispatcher queue implementation and auparse feed parser. Header installation exposes the public API to plugin authors.

Risks and test signals: library ABI versioning and link dependencies are the main risk areas. Missing common/lib include paths or queue linkage would fail build. Tests under `auplugin/test` validate exported fgets and stats behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auplugin/Makefile.am -->
