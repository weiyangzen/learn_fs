# sources/security-integrity/audit-userspace/audisp/plugins/syslog/Makefile.am

Purpose: builds and installs the `audisp-syslog` plugin and plugin config.

Important APIs and data: defines `audisp_syslog_SOURCES = audisp-syslog.c`, PIE/RELRO flags, libaudit/auparse/auplugin dependencies, installed `syslog.conf`, and man page.

Control flow: automake install hook creates plugins.d and installs config with mode 0640.

State and persistence: build/install metadata only.

Dependencies and integration: integrates syslog plugin with audit dispatcher and build system.

Risks: command-line args are supplied by config, so packaging must keep config and binary behavior aligned.

Test signals: build/install checks and dispatcher startup tests.
