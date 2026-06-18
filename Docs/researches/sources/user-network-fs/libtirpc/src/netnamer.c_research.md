## sources/user-network-fs/libtirpc/src/netnamer.c

Purpose: Converts Secure RPC network names back to Unix credentials or hostnames, using `/etc/netid`, optional NIS, and local passwd/group databases.

Important APIs and control flow: `netname2user` first tries `getnetid`; a matching record yields uid, gid, and supplementary groups from colon/comma-separated fields. If no netid entry exists, it parses `unix.<uid>@<domain>`, verifies the default domain, looks up passwd by uid, and derives groups via `_getgroups`. `netname2host` similarly honors netid host records beginning with `0:`, otherwise parses `unix.<host>@<domain>`. `getnetid` scans `/etc/netid`, supports `+` NIS inclusion when built with YP, and returns copied map values.

State and persistence: No long-lived local state. It reads `/etc/netid`, passwd/group databases, default domain, and optional NIS maps on demand.

Dependencies and integration: Reverse side of `netname.c`; used by AUTH_DES credential mapping.

Risks and test signals: Fixed 1024-byte buffers and `strcpy` assume map values fit. Tests should cover netid records, fallback parsing, wrong domain rejection, duplicate group filtering, too many groups, host records, and YP-disabled `+`.
