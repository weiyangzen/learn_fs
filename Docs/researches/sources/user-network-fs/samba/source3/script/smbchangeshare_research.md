# sources/user-network-fs/samba/source3/script/smbchangeshare

Purpose: example Samba selftest helper for the `change share command` hook.

Important APIs, types, and functions: reads config, share name, path, comment, max connections, and CSC policy; calls `net conf setparm` for `path`, `comment`, `max connections`, and `csc policy`.

Control flow: sequentially set each parameter, checking the return code after every command and exiting immediately on failure.

State and persistence: mutates Samba share configuration.

Dependencies and integration: requires `$BINDIR/net` and writable `net conf` backend.

Risks: unquoted `$NETCONF` command prefix has path-splitting risk. Partial updates are possible because earlier parameter changes are not rolled back after a later failure.

Test signals: successful full update, each individual setparm failure, partial update behavior, and CSC policy validation.
