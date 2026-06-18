# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.h

## Role

Defines the resolver mesh data structures and public functions used by workers and modules to create, share, run, attach, detach, answer, and delete active DNS query states.

## Main Types

- `struct mesh_area`: per-worker mesh root containing module stack copy, module environment, runnable/all query rbtrees, reply/detached counters, jostle/forever lists, stats, histogram, query-buffer backup, and response-IP/RPZ flags.
- `struct mesh_state`: one active query state, with rb-tree nodes, embedded `module_qstate`, reply/callback lists, first-reply time, super/sub rbtree sets, activation count, linked-list membership, uniqueness marker, and sent flag.
- `struct mesh_state_ref`: rbtree reference wrapper used for super/sub dependency sets.
- `struct mesh_reply`: per-client reply metadata: copied comm reply, EDNS, start time, original ID/flags/qname, local alias copy, and optional HTTP/2 stream.
- `mesh_cb_func_type` and `struct mesh_cb`: callback consumer interface and callback metadata.

## Constants

- `MESH_MAX_ACTIVATION`: max module activations before treating a state as looping.
- `MESH_MAX_SUBSUB`: max recursive dependency scan size for cycle detection.

## API Categories

- Worker-facing entry points: `mesh_create`, `mesh_delete`, `mesh_new_client`, `mesh_new_callback`, `mesh_new_prefetch`, `mesh_report_reply`.
- Module environment helpers: `mesh_detach_subs`, `mesh_attach_sub`, `mesh_add_sub`, `mesh_query_done`, `mesh_walk_supers`, `mesh_state_delete`.
- Mesh internals exposed for implementation/tests: `mesh_state_create`, `mesh_state_make_unique`, `mesh_state_cleanup`, `mesh_delete_all`, `mesh_area_find`, `mesh_state_attachment`, `mesh_state_add_reply`, `mesh_state_add_cb`, `mesh_run`.
- Diagnostics/accounting: `mesh_stats`, `mesh_stats_clear`, `mesh_log_list`, `mesh_get_mem`.
- Dependency/list/limit helpers: `mesh_detect_cycle`, `mesh_state_compare`, `mesh_state_ref_compare`, `mesh_make_new_space`, `mesh_list_insert`, `mesh_list_remove`, `mesh_state_remove_reply`, `mesh_jostle_exceeded`.
- Serve-expired helpers: `mesh_serve_expired_callback`, `mesh_serve_expired_lookup`, `mesh_respond_serve_expired`.
- Callback removal: `mesh_remove_callback`.

## Contracts and Semantics

- Mesh states aggregate equivalent queries unless EDNS or client policy requires uniqueness.
- Reply states are bounded and may be split into run-to-completion "forever" states and jostle-eligible states.
- Subquery edges must remain symmetric between a super state's `sub_set` and a sub state's `super_set`.
- Reply consumers and callback consumers both contribute to reply address accounting.

## Research Notes

- The header documents that each `mesh_state` is region-allocated using the qstate region; all dependent structures are expected to share that lifetime.
- The interface is central to module execution: modules attach subqueries, wait, finish, and are informed through this mesh rather than directly managing recursion scheduling.
