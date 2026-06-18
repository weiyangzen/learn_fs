# sources/user-network-fs/samba/source4/libcli/raw/clierror.c

Purpose: exposes simple error inspection helpers for the raw SMB client tree.

Important APIs: `smbcli_errstr()` maps the transport's last error type to a string; `smbcli_nt_error()` maps it to an `NTSTATUS`; `smbcli_is_error()` returns whether that status is an error.

Control flow: functions inspect `tree->session->transport->error.etype` and return SMB NT status, generic unsuccessful for socket/NBT errors, OK for no error, or string labels for non-SMB errors.

State and persistence: reads the in-memory last-error state maintained by transport request handling. No persistence.

Dependencies and integration: depends on raw libcli structures and raw prototypes. Used by higher-level raw callers after request receive/destruction.

Risks: callers passing null or partially torn-down tree/session/transport will crash. Socket and NBT errors lose detailed status. Test signals include SMB error propagation, socket/NBT error mapping, no-error mapping, and use after failed request paths.
