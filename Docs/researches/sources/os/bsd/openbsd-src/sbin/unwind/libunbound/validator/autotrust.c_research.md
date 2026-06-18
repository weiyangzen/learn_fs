# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.c

## Purpose
Implements RFC5011 automated DNSSEC trust anchor management for Unbound. It loads, persists, probes, verifies, updates, revokes, and removes trust anchor keys using the RFC5011 state table.

## Main Responsibilities
- Maintains global probe ordering in `autr_global_data.probe`.
- Parses auto-trust-anchor files, including metadata comments, `$ORIGIN`, multiline DNS records, DS/DNSKEY filtering, and per-file single-trust-point enforcement.
- Assembles valid autotrust key lists into heap-backed `ub_packed_rrset_key` DS/DNSKEY rrsets for validator use.
- Writes updated autotrust files atomically through a unique temporary file, flush/fsync, close, then rename.
- Verifies probed DNSKEY rrsets against current trust anchors.
- Detects self-signed revoked DNSKEYs and transitions stored keys into revoked/removed states.
- Implements add, delete, missing, revoked, and keep-missing holddown behavior.
- Schedules DNSKEY probe queries through the mesh and resets worker timers.

## Important State
`struct autr_ta` stores one tracked key and its RFC5011 state, pending count, last-change time, fetched marker, and revoked marker. `struct autr_point_data` stores per-trust-point file path, probe-tree node, key list, probe timing, query intervals, failure count, and revoked flag.

## Key Functions
- `autr_global_create` / `autr_global_delete`: allocate and initialize the global probe rbtree.
- `probetree_cmp`: orders trust points by `next_probe_time`, then by anchor identity.
- `autr_read_file`: reads persisted autotrust state and assembles rrsets.
- `parse_comments`: extracts per-key `state=`, `count=`, and `lastchange=` metadata.
- `autr_write_file`: persists state via temp-file replacement.
- `autr_assemble`: builds DS and DNSKEY packed rrsets from current key states.
- `verify_dnskey`: validates probed DNSKEY rrsets against trust anchor material.
- `check_contains_revoked`: finds self-signed revoked KSKs and marks stored keys revoked.
- `update_events`: notes fetched KSKs, adds new keys, bootstraps DNSKEYs from matching DS records, and updates query/retry intervals.
- `anchor_state_update`: applies the RFC5011 state transition matrix for each key.
- `autr_process_prime`: central processing path after a DNSKEY probe result.
- `probe_anchor`, `todo_probe`, `autr_probe_timer`: drive scheduled active DNSKEY probes.

## Control Flow
Startup/config loading calls `autr_read_file`, which creates or finds the trust point, loads keys, parses RFC5011 metadata, and assembles rrsets. Runtime probing calls `autr_probe_timer`, which selects due trust points, moves their next probe to a retry interval, clears cached DNSKEY/key-cache entries, and submits an active DNSKEY query. When the DNSKEY set is processed by `autr_process_prime`, the code checks revoked keys, verifies the DNSKEY set, updates fetched/new-key state, applies holddowns, cleans removed keys, schedules the next probe, writes the file, and reassembles rrsets if changed.

## Dependencies and Integration
Integrates tightly with `val_anchor`, `val_sigcrypt`, `val_utils`, `val_kcache`, rrset cache, mesh query service, regional scratch allocation, Unbound config, random jitter, and sldns wire/text conversion helpers. It stores autotrust points inside the same `val_anchors` tree as static trust anchors, with additional probe-tree membership.

## Notable Constraints and Risks
- File parsing is permissive enough to continue after bad individual records, but the final trust point must exist.
- Auto-trust files may contain only one anchor name/class; mixed names are rejected.
- `autr_write_file` uses fatal exits for persistent write/rename failure, reflecting that broken trust-anchor persistence is treated as critical.
- The implementation tracks ZSK-to-KSK bootstrap behavior for initially configured ZSKs, which is subtle and security-sensitive.
- Lock ordering is carefully managed: anchor tree lock and trust-point locks are released/reacquired in paths that mutate probe trees or run mesh queries.
