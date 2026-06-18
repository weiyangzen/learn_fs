# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.h

Purpose: declares z/OS remote logging helpers and debug macros.

Important APIs and data: declares external `pid_t mypid`, log functions, debug BER functions, and `DEBUG`-controlled macros `log_debug`, `debug_bv`, and `debug_ber`.

Control flow: macro control either routes debug calls to real functions or removes them.

State and persistence: relies on process-global `mypid`; no local state.

Dependencies and integration: includes zOS LDAP types, syslog, unistd, and lber, so consumers get BER type declarations.

Risks: including `zos-remote-ldap.h` here creates a broad dependency from logging to LDAP headers. Debug macros with empty replacement can hide side effects in arguments if callers rely on them.

Test signals: compile with and without `DEBUG`, and verify callers define `mypid`.
