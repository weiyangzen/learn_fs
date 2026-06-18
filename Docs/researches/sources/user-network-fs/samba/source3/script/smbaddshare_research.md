# sources/user-network-fs/samba/source3/script/smbaddshare

Purpose: example Samba selftest helper for the `add share command` configuration hook.

Important APIs, types, and functions: consumes config path, share name, path, comment, and max connections. Uses `$BINDIR/net --configfile=$CONF conf addshare` and `setparm`.

Control flow: add a share with `writeable=no` and `guest_ok=no`; if successful, set `max connections`; exit with the failing return code on error.

State and persistence: mutates Samba registry/configuration through `net conf`.

Dependencies and integration: requires `$BINDIR/net` and a writable Samba config backend. Intended mainly for selftest.

Risks: `$NETCONF` is expanded unquoted as a command prefix, so spaces in `$BINDIR` or config paths can break. Real deployments must review defaults before use.

Test signals: successful add, failed add, failed setparm, max connection value handling, and config paths with special characters.
