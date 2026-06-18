# sources/sync-backup/rsync/uidlist.c

Purpose: maps user/group IDs and names between sender and receiver, including explicit `--usermap`/`--groupmap`, numeric-id handling, ACL integration, and non-root group-skip behavior.

Important APIs/types/functions: `struct idlist` stores original ID/name/range/match flags and mapped ID. `uid_to_user()`, `gid_to_group()`, `user_to_uid()`, and `group_to_gid()` wrap system databases or `namecvt_call()`. `add_uid()`/`add_gid()` collect sender-side IDs; `send_id_lists()` serializes mappings; `recv_user_name()`, `recv_group_name()`, and `recv_id_list()` receive and apply mappings to flist entries. `parse_name_map()` parses number ranges, exact names, and wildcard names. `match_uid()`/`match_gid()` lazily map IDs and cache the last lookup. `getallgroups()` populates supplemental groups when available.

Control flow and state: four linked lists track transmitted uid/gid lists and configured maps. Sender transmits non-zero IDs plus optional ID-0 names. Receiver reads lists when preserving uid/gid/acls and `numeric_ids <= 0`, resolves names locally unless numeric mode suppresses names, then rewrites flist owner/group fields. Non-root receivers mark disallowed groups with `FLAG_SKIP_GROUP`.

Dependencies and integration: depends on passwd/group APIs, rsync varint I/O, wildcard matching, ACL ID matching, global option state, and name-converter subprocess support. Risks include syntax errors in map parsing, ID overflow detection in `id_parse()`, linked-list lookup cost for very large ID sets, and platform group-list quirks. Test signals are ownership-preservation, ACL, fake-super, and daemon tests rather than a single dedicated unit in this subset.
