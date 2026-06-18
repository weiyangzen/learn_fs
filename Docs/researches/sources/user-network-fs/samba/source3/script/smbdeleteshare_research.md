# sources/user-network-fs/samba/source3/script/smbdeleteshare

Purpose: example Samba selftest helper for the `delete share command` hook.

Important APIs, types, and functions: reads config and share name, builds `$BINDIR/net --configfile=$CONF conf`, and runs `delshare`.

Control flow: execute `net conf delshare`, report and exit with the command return code on failure.

State and persistence: deletes a Samba share from the configured backend.

Dependencies and integration: requires `$BINDIR/net`; intended for selftest or carefully adapted deployments.

Risks: unquoted `$NETCONF` command prefix can break on spaces. It performs irreversible share removal without confirmation.

Test signals: successful deletion, nonexistent share, permission/config failures, and path quoting cases.
