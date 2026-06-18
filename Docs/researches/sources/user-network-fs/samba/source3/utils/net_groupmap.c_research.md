# sources/user-network-fs/samba/source3/utils/net_groupmap.c

Purpose: implements `net groupmap`, a local passdb-backed tool for mapping NT group SIDs to Unix groups and managing alias membership records.

Important APIs/types/functions: `net_groupmap()` dispatches `add`, `modify`, `delete`, `set`, `cleanup`, `addmem`, `delmem`, `listmem`, `memberships`, and `list`. Helpers include `get_sid_from_input()` and `print_map_entry()`. It uses passdb group mapping and alias APIs.

Control flow: list parses filters and either prints one mapping or enumerates all. Add parses RID/SID, Unix group, NT group, comment, and type, validates Unix group, allocates or derives RID, composes SID if needed, and calls `add_initial_entry()`. Modify resolves existing map by SID/name, applies type/comment/name/gid changes, and updates passdb. Delete resolves and removes. Set is add-or-update using global options. Alias commands parse SIDs and add/delete/list memberships.

State and persistence: mutates local passdb group mapping and alias membership records. `cleanup` deletes mappings outside local SAM and BUILTIN SID namespaces. List/memberships are read-only.

Dependencies/integration: depends on Unix group lookup, passdb, domain SID helpers, SID parsing/formatting, and `net_context` option fields.

Risks: auth-critical destructive local state. `modify` rejects omitted `type=` because `sid_type` remains `SID_NAME_UNKNOWN`, despite usage marking type optional. RID allocation fallback can create algorithmic mappings. Cleanup intentionally deletes foreign mappings.

Test signals: add explicit RID/SID and automatic RID on different passdb backends; verbose list; modify with/without type; delete by name/SID; set with `-L`/`-D`; cleanup local/builtin/foreign entries; alias membership commands.
