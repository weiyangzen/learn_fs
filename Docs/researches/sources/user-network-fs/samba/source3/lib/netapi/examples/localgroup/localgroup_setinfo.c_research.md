# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_setinfo.c

Purpose: Demonstrates updating local group metadata with `NetLocalGroupSetInfo()`.

Important APIs/types/functions: Supports levels 0, 1, and 1002 using `LOCALGROUP_INFO_0`, `_1`, and `_1002`; accepts `--newname` and `--newcomment`.

Control flow: Parses hostname/group/level/options, verifies enough input for the requested level, fills the structure, calls `NetLocalGroupSetInfo()`, reports `parm_err` failures, and cleans up.

State and persistence behavior: Mutates local group name/comment state.

Dependencies and integration points: Paired with `localgroup_getinfo`.

Risks: Rename/comment support may vary by server. The sample does not prefetch existing values, so omitted fields may become NULL where the level uses them.

Test signals: Change a disposable local group's comment/name and verify by getinfo and enum.
