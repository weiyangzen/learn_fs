# sources/user-network-fs/samba/source3/nmbd/nmbd_workgroupdb.c

Purpose: maintains nmbd's in-memory NetBIOS workgroup database per subnet. It creates, finds, links, expires, and logs `struct work_record` instances and seeds the local workgroup with Samba's own server records and registered NetBIOS group names.

Important APIs and flow: `create_workgroup_on_subnet()` calls the private `create_workgroup()` initializer and `add_workgroup()` list linker. `find_workgroup_on_subnet()` normalizes names through `name_to_unstring()` before scanning a subnet list. `initiate_myworkgroup_startup()` only acts for `lp_workgroup()`, may request an election when `lp_preferred_master()` and `lp_local_master()` allow it, registers `<00>` and `<1e>` names, and creates local-list-only server records for every `my_netbios_names()` entry. `expire_workgroups_and_servers()` first expires server records, then removes dead non-permanent empty workgroups.

State and persistence: the file owns process-local linked-list state hanging off `struct subnet_record`; no durable database is written here. `workgroup_count` allocates stable-ish tokens, reusing an existing token for the same workgroup name on another subnet. TTL is represented as `death_time = now + ttl * 3`, except `PERMANENT_TTL`.

Dependencies and integration: depends on nmbd subnet/server-list helpers, NetBIOS registration, Samba loadparm settings, name conversion wrappers, and browser election constants. The `work_changed` flag signals later announce/sync work.

Risks: list mutation and raw allocation require careful ordering; a failed server cleanup can prevent freeing a workgroup. Name truncation can alias long workgroup names. Election behavior depends on global loadparm state at creation/startup time.

Test signals: exercise long-name truncation, token reuse across subnets, TTL refresh/removal, preferred-master startup, and dumping at both forced and debug-level paths.
