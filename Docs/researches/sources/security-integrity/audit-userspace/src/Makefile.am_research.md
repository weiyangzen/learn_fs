# sources/security-integrity/audit-userspace/src/Makefile.am

Purpose: Automake build definition for audit-userspace command binaries.

Important targets: builds `auditd`, `auditctl`, `aureport`, and `ausearch`; defines source lists, PIE/RELRO flags for auditd/auditctl, headers, subdirectory `test`, and `libev/libev.a` helper target.

Control flow: build-system only. `auditctl_SOURCES` includes `auditctl.c`, `auditctl-llist.c`, `delete_all.c`, and `auditctl-listing.c`; `auditctl_LDADD` links libaudit, auparse, and common libraries.

State and persistence: no runtime state; controls build/install artifacts.

Dependencies and integration: depends on generated config, libaudit, auparse, audisp, common, libev, optional listener support, pthread/math/GSS/libwrap for auditd.

Risks and test signals: source list drift breaks builds or omits files from binaries. Test with full Autotools build and `make check`.
