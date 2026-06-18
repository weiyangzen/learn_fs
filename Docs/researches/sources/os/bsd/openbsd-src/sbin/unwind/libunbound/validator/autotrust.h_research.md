# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/validator/autotrust.h

## Purpose
Declares the data structures and public functions for RFC5011 automated trust anchor maintenance.

## Main Types
- `autr_state_type`: RFC5011 states `START`, `ADDPEND`, `VALID`, `MISSING`, `REVOKED`, and `REMOVED`.
- `struct autr_ta`: metadata for one tracked trust anchor RR, including wire RR, lengths, last change, state, pending count, fetched flag, and revoked flag.
- `struct autr_point_data`: per-trust-point autotrust state, including backing file path, probe-tree node, key list, last query/success times, next probe time, query/retry intervals, failure counter, and trust-point revoked flag.
- `struct autr_global_data`: global rbtree of autotrust anchors sorted by next probe time.

## Public API
- Global lifecycle: `autr_global_create`, `autr_global_delete`.
- Introspection/timers: `autr_get_num_anchors`, `autr_probe_timer`, `probetree_cmp`.
- Persistence: `autr_read_file`, `autr_write_file`.
- Trust point lifecycle: `autr_point_delete`.
- Probe processing: `autr_process_prime`, `probe_answer_cb`.
- Debug output: `autr_debug_print`.

## Integration
The header bridges validator trust-anchor storage (`val_anchors`, `trust_anchor`) with module runtime state (`module_env`, `module_qstate`, `val_env`) and packed DNS rrsets.

## Notable Constraints
The API exposes internal structures because autotrust state is embedded directly in `struct trust_anchor`. Callers must observe locking rules from `val_anchor` when reading or mutating these fields.
