# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/val_anchor.c

## Purpose
Implements validator trust anchor storage. It loads static trust anchors, insecure domains, BIND-style trusted-key files, and autotrust files into an rbtree keyed by class and domain name, then assembles DS/DNSKEY rrsets for validation.

## Main Responsibilities
- Creates/deletes `val_anchors` storage and all contained `trust_anchor` objects.
- Maintains parent pointers so lookup can find the closest enclosing trust anchor.
- Stores DS/DNSKEY trust anchor records from strings, zone files, and BIND `trusted-keys` syntax.
- Stores insecure points as trust anchors with no DS/DNSKEY records.
- Supports wildcard expansion for `trusted-keys-file` when `glob` is available.
- Assembles `ta_key` linked-list contents into `ub_packed_rrset_key` DS/DNSKEY rrsets.
- Filters out trust anchors whose DS/DNSKEY algorithms are all unsupported.
- Adds/deletes insecure points dynamically.
- Exposes keytag listing and keytag lookup helpers.

## Key Functions
- `anchors_create` / `anchors_delete`: allocate and free trust-anchor store plus autotrust global state.
- `anchor_cmp`: canonical rbtree ordering by class and domain-label order.
- `anchors_init_parents_locked`: recomputes closest parent pointers after tree mutation.
- `anchor_find` and `anchors_lookup`: exact and closest-enclosing lookup, returning locked anchors.
- `anchor_store_str`, `anchor_read_file`: parse textual DS/DNSKEY records and store them.
- `anchor_read_bind_file`, `process_bind_contents`: parse BIND `trusted-keys { ... };` format.
- `anchors_apply_cfg`: applies all trust-anchor-related configuration sources.
- `anchors_assemble_rrsets`: assembles usable rrsets and removes anchors with no supported algorithms.
- `anchors_add_insecure` / `anchors_delete_insecure`: dynamic insecure point management.
- `anchor_list_keytags`, `anchor_has_keytag`: keytag utilities.
- `anchors_swap_tree`: swaps anchor/probe trees with preallocated data.

## Control Flow
Configuration application inserts insecure LAN zones and `domain-insecure` entries first, then loads trust-anchor files, BIND trusted-key files, inline trust-anchor strings, and finally autotrust files. Static anchors are then assembled and parent pointers are initialized. Lookup later uses the sorted tree and parent pointers to return the closest applicable trust anchor for a query name/class.

## Dependencies and Integration
Uses `val_sigcrypt` for algorithm/keytag checks, `autotrust` for RFC5011 files, sldns parsing helpers, Unbound lock/rbtree utilities, AS112 insecure LAN zones, and packed rrset structures.

## Notable Constraints and Risks
- The assembled rrsets reuse `ta_key->data` pointers; deletion paths must avoid double-free by only freeing wrapper arrays/data structures appropriately.
- BIND parser is purpose-built for trusted-key clauses rather than a full named.conf parser.
- Lookup returns locked anchors, so callers must unlock.
- Unsupported algorithms are warned about; anchors with no supported material are removed from the tree.
