# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.h

## Purpose
Defines trust anchor storage types and declares validator trust-anchor management functions.

## Main Types
- `struct val_anchors`: global trust-anchor store with a lock, canonical rbtree, and autotrust global data.
- `struct ta_key`: one stored DS or DNSKEY trust anchor rdata blob.
- `struct trust_anchor`: one anchor point keyed by name/class, with lock, parent pointer, key list, optional autotrust data, DS/DNSKEY counts, assembled rrsets, and class.

## Public API
- Store lifecycle: `anchors_create`, `anchors_delete`.
- Configuration: `anchors_apply_cfg`.
- Parent maintenance: `anchors_init_parents_locked`.
- Lookup: `anchors_lookup`, `anchor_find`.
- Parsing/storage: `anchor_store_str`.
- Memory accounting: `anchors_get_mem`.
- Ordering: `anchor_cmp`.
- Insecure points: `anchors_add_insecure`, `anchors_delete_insecure`.
- Keytag helpers: `anchor_list_keytags`, `anchor_has_keytag`.
- Discovery/swap: `anchors_find_any_noninsecure`, `anchors_swap_tree`.

## Locking Model
The header documents the important ordering rule: lock the global tree first, find an anchor, then lock the anchor. To delete an anchor, callers may need to release and look up again because parent pointers and tree membership are protected globally.

## Integration
This is the core shared trust-anchor representation used by static anchors, autotrust, and the DNSSEC validator's chain-building logic.

## Notable Constraints
`trust_anchor` contains both static-anchor and autotrust fields. Code must distinguish static anchors from autotrust anchors by checking `ta->autr`.
