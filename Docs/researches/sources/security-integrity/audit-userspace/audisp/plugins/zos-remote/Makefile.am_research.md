# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/Makefile.am

Purpose: builds and installs the z/OS remote audit dispatcher plugin.

Important APIs and data: defines `audispd-zos-remote` sources (`zos-remote-plugin.c`, log, LDAP, config, queue), headers, LDAP/LBER/pthread dependencies, PIE/RELRO flags, and config files `zos-remote.conf` and `audispd-zos-remote.conf`.

Control flow: install hook creates `/etc/audit` and plugins.d destinations and installs both configs with mode 0640.

State and persistence: build/install metadata; runtime queue/config state lives in other zOS plugin files.

Dependencies and integration: integrates with auparse and LDAP libraries; dispatcher registration points to this binary with config path arg.

Risks: this subset does not include the main plugin/queue source, so behavior research here depends on referenced files. LDAP library availability controls build.

Test signals: build/link tests and install artifact checks.
