# sources/security-integrity/audit-userspace/audisp/plugins/remote/Makefile.am

Purpose: builds and installs the `audisp-remote` plugin, its configs, man pages, headers, and queue tests.

Important APIs and data: defines `sbin_PROGRAMS = audisp-remote`, `check_PROGRAMS = test-queue`, source lists for the daemon and test, installed config paths, PIE/RELRO flags, and dependencies on libaudit, aucommon, auplugin, optional GSS libs, and cap-ng.

Control flow: automake install hooks create `/etc/audit` and `/etc/audit/plugins.d` targets with mode 0640 config files; uninstall removes them.

State and persistence: no runtime state, but build choices enable persistent queue and remote transport code.

Dependencies and integration: connects source files `audisp-remote.c`, `remote-config.c`, and `queue.c` to the audit userspace build and test system.

Risks: path/install mode assumptions matter for later config permission checks. Missing optional GSS or ASAN flags changes compiled behavior.

Test signals: `make check` runs `test-queue`; install verification should check config locations and modes.
