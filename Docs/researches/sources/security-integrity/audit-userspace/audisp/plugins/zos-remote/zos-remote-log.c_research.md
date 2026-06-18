# sources/security-integrity/audit-userspace/audisp/plugins/zos-remote/zos-remote-log.c

Purpose: centralizes z/OS remote plugin syslog logging and optional BER debug dumps.

Important APIs and data: implements `log_err`, `log_warn`, `log_info`, `_log_debug`, `_debug_ber`, and `_debug_bv`. `vlog_prio` prefixes messages with `pid=<mypid>`.

Control flow: variadic public log functions delegate to `vlog_prio`. Debug BER helpers flatten BER or iterate berval bytes into a hex dump and log it through debug logging.

State and persistence: no owned persistent state; uses external `mypid` and syslog.

Dependencies and integration: depends on `zos-remote-log.h`, auparse/lber BER types, and syslog. Debug macros in the header compile debug calls away unless `DEBUG` is defined.

Risks: `_debug_bv` calls `log_debug(out)` with the hex string as a format string, so percent bytes in debug output would be interpreted if present; hex output only uses digits/spaces in current construction. `asprintf` failures drop log messages silently.

Test signals: debug-enabled builds should verify prefixing and BER hex output; non-debug builds should compile out debug macros.
