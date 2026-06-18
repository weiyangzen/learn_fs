# sources/user-network-fs/samba/source3/utils/net_afs.h

Purpose: declares optional AFS command entry points for `net_afs.c` and command registration.

Important APIs/types/functions: declares `net_afs_usage()`, `net_afs_key()`, `net_afs_impersonate()`, and `net_afs()`, all taking `struct net_context *`, `argc`, and `argv`.

Control flow: no runtime logic; it only exposes prototypes behind `_NET_AFS_H_`.

State and persistence: none directly; implementations can persist AFS keys and kernel tokens.

Dependencies/integration: requires `struct net_context` visibility from prior includes and is included by AFS command implementation.

Risks: declarations are unconditional while implementation is under `WITH_FAKE_KASERVER`; build wiring must avoid unresolved references in disabled builds.

Test signals: compile with/without fake KASERVER; include-order checks; linkage from command table.
