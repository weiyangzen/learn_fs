# sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsset.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/user/user_modalsset.c

Purpose: Demonstrates setting user/domain modal policy with `NetUserModalsSet()`.

Important APIs/types/functions: Supports levels 0, 1, 2, 3, and single-parameter levels 1001-1007 through `USER_MODALS_INFO_*` structures.

Control flow: Parses hostname, level, and numeric/string policy values, fills the matching modal structure, calls `NetUserModalsSet()`, reports `parm_err`, and cleans up.

State and persistence behavior: Mutates persistent account/domain policy on the target server/domain.

Dependencies and integration points: Paired with `user_modalsget`.

Risks: Policy changes are security-sensitive and global. Numeric parsing is weak, and some case labels are accepted without fully populated structures.

Test signals: Apply policy changes only in isolated domains, then verify exact fields with `user_modalsget`.
