# sources/user-network-fs/nfs-ganesha/src/RPCAL/gss_extra.c

Purpose: provides small GSS/RPCSEC_GSS utility functions for logging and debugging.

Important APIs and types: `log_sperror_gss()` converts GSS major/minor status values into a combined string, and `str_gc_proc()` maps `rpc_gss_proc_t` values to symbolic names.

Control flow: `log_sperror_gss()` calls `gss_display_status()` first for the GSS major code and then for the mechanism minor code, formats fallback messages when translation fails, and releases GSS buffers. `str_gc_proc()` switches over RPCSEC_GSS procedure constants and returns `"unknown"` for unrecognized values.

State and persistence: no persistent state. It writes into caller-supplied `outmsg`.

Dependencies and integration points: supports both Heimdal and non-Heimdal include paths, uses GSSAPI, RPC auth GSS types, and Ganesha logging-related headers. Called by authentication paths that need human-readable GSS diagnostics.

Risks: `log_sperror_gss()` uses `sprintf()` with no explicit output buffer length, so caller buffer sizing is critical. It only consumes one display-status message from each status chain, not necessarily all continuation messages. Returned strings from `str_gc_proc()` must remain aligned with RPCSEC_GSS constants.

Test signals: translate known major/minor GSS failures, force major/minor display failure paths, validate buffer sizing at call sites, and cover all RPCSEC_GSS procedure enum values.
