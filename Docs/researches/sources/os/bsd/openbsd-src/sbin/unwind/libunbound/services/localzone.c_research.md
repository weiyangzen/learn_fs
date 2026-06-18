# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/localzone.c

## Role

Implements Unbound's local authoritative zone service. It parses and stores configured `local-zone` and `local-data` entries, adds default special/reverse/AS112 zones, supports tags and per-netblock overrides, answers matching queries locally, and supports dynamic add/delete of zones and records.

## Storage Model

- `local_zones_create` initializes a locked rbtree of `local_zone` objects.
- Each `local_zone` owns a regional allocator for all local data, an rbtree of `local_data` names, linked `local_rrset` entries per name, optional tag bitmap, optional address override tree, and cached SOA pointers for negative answers.
- `local_zone_cmp` sorts zones by DNS class and hierarchical dname order; `local_data_cmp` sorts data names canonically.
- Parent pointers are maintained by `lz_init_parents`, `find_closest_parent`, and dynamic update helpers so lookup can climb from closest less/equal rbtree entries to covering zones.

## Configuration Loading

- `lz_enter_zone` parses textual zone name/type and inserts a zone, returning it write-locked.
- `lz_enter_rr_str` parses RR strings, finds a covering zone, and inserts data.
- `local_zone_enter_defaults` adds built-in localhost, reverse localhost, RFC special-use, and AS112 empty zones unless disabled or excluded by `nodefault`.
- `lz_setup_implicit` creates transparent zones for `local-data` entries without explicit covering `local-zone` statements, including handling non-IN classes by repeating setup.
- `lz_enter_zone_tags` and `lz_enter_overrides` apply tag bitmaps and netblock-specific local-zone type overrides.
- `local_zones_apply_cfg` orchestrates explicit zones, defaults, overrides, implicit zones, parent setup, tags, data insertion, and cleanup of consumed config lists.

## Record Handling

- `rrstr_get_rr_content` and `get_rr_nameclass` parse text RRs into wire format and expose owner/type/class/TTL/RDATA.
- `new_local_rrset`, `rrset_insert_rr`, and `local_zone_enter_rr` build packed rrset structures in the zone region.
- Duplicate RRs are ignored by content comparison.
- Redirect zones reject incompatible CNAME coexistence and require data at the zone apex.
- SOA records at the zone apex are tracked in `z->soa`, and `lz_mark_soa_for_zone` builds an artificial `soa_negative` RRset with TTL clamped to SOA.MINIMUM for negative responses.
- Empty nonterminals are created recursively by `lz_find_create_node`.

## Query Answering

- `local_zones_answer` first checks view-local zones, honors `noview`, then falls back to global tagged lookup.
- `lz_type` applies per-client netblock overrides before tag-action overrides.
- `local_data_answer` returns exact local data, redirect apex data rewritten to the query name, tag-specific redirect data, or deferred local CNAME alias state.
- Wildcard CNAME targets are synthesized into per-query local aliases and checked for maximum DNS name length.
- `local_zones_zone_answer` handles zone-type fallback behavior:
  - `deny`/`always_deny`/`inform_deny`: drop by clearing the output buffer.
  - `refuse`/`always_refuse`: authoritative REFUSED.
  - `static`, `redirect`, `inform_redirect`, `always_nxdomain`, `always_nodata`, UDP `truncate`: authoritative NXDOMAIN/NODATA/truncated responses, using negative SOA when available.
  - `transparent`, `typetransparent`, `inform`, `always_transparent`, `block_a`: pass through as appropriate.
  - `always_null`: synthetic `0.0.0.0`, `::0`, or NODATA.
- Local replies run inplace reply callbacks and may attach EDE options when configured.

## Dynamic Updates and Maintenance

- `local_zones_add_zone` and `local_zones_del_zone` update the zone tree and repair child parent pointers.
- `local_zones_add_RR` creates a transparent zone if no covering zone exists, then inserts the RR.
- `local_zones_del_data` removes DS separately with DS lookup semantics, clears other rrsets, resets zone SOA pointers when needed, and prunes terminal empty-nonterminal nodes.
- `local_zones_get_mem` accounts zone structure, names, taglist, and regional allocations.
- `local_zones_swap_tree` swaps rbtrees for prebuilt data replacement.

## Research Notes

- Locking is layered: the global zone tree lock protects tree membership and structural zone fields; each zone lock protects per-zone data and runtime metadata.
- Regional allocation simplifies lifetime but means dynamic deletions do not reclaim per-record memory until the entire zone is replaced or deleted.
- DS lookups intentionally move to a parent zone for normal add/remove semantics, with a special answering exception for `always_refuse` at a zone cut.
