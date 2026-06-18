# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.h

## Role

Public interface and data model for the local authoritative zone service implemented in `localzone.c`.

## Main Types

- `enum localzone_type`: defines all local-zone behaviors: unset, deny, refuse, static, transparent, typetransparent, redirect, nodefault, inform variants, always-transparent/refuse/nxdomain/nodata/deny/null, noview, truncate, and invalid.
- `struct local_zones`: locked rbtree of local zones.
- `struct local_zone`: one authoritative local zone, including rbtree node, parent pointer, wire-format name, class, lock, behavior type, tag bitmap, optional address override tree, regional allocator, data tree, and SOA/negative-SOA cached rrsets.
- `struct local_data`: one domain name within a local zone, with exact wire name and linked rrsets; `rrsets == NULL` represents an empty nonterminal.
- `struct local_rrset`: linked wrapper around `ub_packed_rrset_key`.
- `struct local_zone_override`: address-tree node mapping client netblocks to override zone type.
- `enum respip_action`: shares values with local-zone types for response-IP/RPZ-style policy actions.

## API Categories

- Lifecycle/config: `local_zones_create`, `local_zones_delete`, `local_zones_apply_cfg`, `local_zone_enter_defaults`.
- Lookup/debug: `local_zones_tags_lookup`, `local_zones_lookup`, `local_zones_find`, `local_zones_find_le`, `local_zones_print`.
- Answering: `local_zones_answer`, `local_zones_zone_answer`, `local_data_answer`.
- Type conversion: `local_zone_str2type`, `local_zone_type2str`.
- Mutation: `local_zones_add_zone`, `local_zones_del_zone`, `local_zones_add_RR`, `local_zones_del_data`, `local_zone_enter_rr`, `local_rrset_remove_rr`.
- Parsing/building helpers: `parse_dname`, `rrstr_get_rr_content`, `rrset_insert_rr`.
- Tag policy: `local_data_find_tag_datas`, `local_data_find_tag_action`.
- Testing/internal exposure: `lz_enter_zone`, `lz_init_parents`.
- Memory/swap: `local_zones_get_mem`, `local_zones_swap_tree`.

## Contracts and Semantics

- Callers must respect locking notes: many lookup and mutation helpers require the zones tree or returned zone to be locked by the caller.
- `local_zones_answer` may return true without an encoded answer when `qinfo->local_alias` is set; the caller must complete and encode the alias chain.
- `local_zones_answer` can signal a deliberate drop by returning true with an empty buffer.
- `local_zone_nodefault` is a configuration-only value, not a serving behavior.

## Research Notes

- The header documents how local aliases are allocated and when callers need deep copies.
- `respip_action` intentionally aliases local-zone behavior values so access-control tag actions can be shared between local zones and response-IP logic.
