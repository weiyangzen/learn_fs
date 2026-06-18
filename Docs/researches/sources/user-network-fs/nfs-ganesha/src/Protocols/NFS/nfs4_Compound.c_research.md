<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_Compound.c -->
# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_Compound.c

## Purpose
Implements the NFSv4 `COMPOUND` procedure dispatcher and lifecycle manager. It validates minor versions and compound shape, dispatches per-op handlers, accounts response sizes/statistics/QoS, handles async resume, maintains NFSv4.1 session replay caching, and frees/copies compound results.

## APIs, Types, and Functions
Major entry points are `nfs4_Compound()`, `process_one_op()`, `complete_op()`, `complete_nfs4_compound()`, `nfs4_compound_resume()`, `nfs4_Compound_FreeOne()`, `release_nfs4_res_compound()`, `nfs4_Compound_Free()`, `compound_data_Free()`, `nfs4_Compound_CopyResOne()`, `xdr_COMPOUND4res_extended()`, and optional `nfs4_qos_compound_cb()`. The central table is `optabv4[]`, mapping opcodes to names, handlers, resume callbacks, free callbacks, response sizes, and required export permission flags.

## Control Flow, State, and Persistence
`nfs4_Compound()` allocates `COMPOUND4res_extended` and `compound_data_t`, validates minor version enablement and RDMA support, copies/validates the tag, extracts client credentials, allocates the response op array, enforces v4.1 first-op/session rules, installs `rq_resume_cb`, and iterates operations. `process_one_op()` enforces position rules for `SEQUENCE`, `BIND_CONN_TO_SESSION`, and `DESTROY_SESSION`, export permission flags, per-session max operations, response room limits, QoS suspension, and handler dispatch. `complete_op()` reads the first status field from the result union, updates response size and per-op stats, and stops the compound on error. Completion caches full or uncached v4.1 slot replies, updates leases, and releases preserved client IDs. `compound_data_Free()` releases current/saved objects, session slots, exports, pNFS DS refs, and file-handle buffers. Persistent state includes slot replay cache entries, lease renewal side effects, and session slot last-request metadata.

## Dependencies and Integration
This file integrates nearly every NFSv4 subsystem: FSAL handles, SAL state/session/clientid management, exports, pNFS, QoS, server stats, LTTng tracing, XDR, and all individual `nfs4_op_*` implementations. It is the authoritative opcode dispatch and cleanup contract for dynamic result memory.

## Risks and Test Signals
Risks include stale `optabv4` metadata, shallow replay-cache copies of results with dynamic memory, response-size underestimation, async resume touching already-resumed requests, slot lock/refcount leaks, incorrect v4.1 compound-shape errors, and missing deep-copy/free support for newer operations. Test signals are pynfs compound/session suites, replay cache tests, async READ/WRITE/LAYOUT operations, response size limit tests, invalid opcode/minor-version/RDMA cases, sanitizer leak checks, and slot cache reference-count tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_Compound.c -->
