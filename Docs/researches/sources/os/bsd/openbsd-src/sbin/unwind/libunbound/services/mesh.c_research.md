# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/mesh.c

## Role

Implements the per-worker resolver mesh: a graph of active DNS query states, shared client replies/callbacks, subquery dependencies, runnable states, module-stack execution, response delivery, stale-answer serving, RPZ/response-IP postprocessing, and mesh statistics.

## State Identity and Creation

- `mesh_state_compare` keys states by uniqueness pointer, priming flag, validation-recursion flag, RD/CD flags, query info, and response-IP client info.
- `client_info_compare` prevents unsafe state sharing when tag lists, tag actions, tag data pointers, or view names differ.
- `mesh_state_create` obtains a regional allocator, copies query name/client info into it, initializes module qstate fields, module ext states, EDNS option lists, and mesh rb-tree nodes.
- `mesh_state_make_unique` disables aggregation by making the state key include its own pointer.

## Mesh Lifecycle and Limits

- `mesh_create` initializes `run` and `all` rbtrees, histogram, query-buffer backup, reply-state limits, jostle timeout, and counters.
- `mesh_delete` and `mesh_delete_all` delete all active states, with `mesh_delete_all` accounting unsent replies as dropped.
- `mesh_make_new_space` enforces `num_queries_per_thread`; it may jostle the oldest eligible reply state, notify superstates with SERVFAIL, delete the state, and restore the incoming query buffer.
- `mesh_jostle_exceeded` checks all active query count against the reply-state limit.

## Client, Callback, and Prefetch Entry Points

- `mesh_new_client` handles incoming client queries:
  - Applies infra wait limits.
  - Reuses an existing mesh state unless EDNS/options require uniqueness.
  - Enforces reply-address limits.
  - Adds `mesh_reply` state, TCP request linkage, HTTP/2 stream linkage, serve-expired timer, wait-limit accounting, and jostle/forever list placement.
  - Starts the run loop for newly created states.
- `mesh_new_callback` attaches callback consumers with similar state reuse/create logic and no reply-count hard limit.
- `mesh_new_prefetch` schedules detached recursive refreshes, forcing RD and optionally preserving ECS/subnet information when compiled with `CLIENT_SUBNET`.
- `mesh_report_reply` converts outbound network completion into module events and resumes the relevant mesh state.

## Dependency Graph

- `mesh_add_sub` finds or creates a subquery state, queues new states in `run`, and checks cycles when reusing an existing state.
- `mesh_attach_sub` attaches super/sub references and updates detached-state accounting.
- `mesh_state_attachment` inserts symmetric region-allocated refs into super `sub_set` and sub `super_set`.
- `mesh_detach_subs` removes all subquery relationships for a qstate and repairs detached counters.
- `mesh_detect_cycle` and helper recursion bound cycle detection by `MESH_MAX_SUBSUB`.
- `mesh_walk_supers` makes superstates runnable, calls module `inform_super`, and copies relevant state upward.

## Module Run Loop

- `mesh_run` repeatedly calls the current module's `operate`, clears transient reply/scratch state, reads module ext state, and delegates transition decisions to `mesh_continue`.
- `mesh_continue` handles:
  - Activation loop guard via `MESH_MAX_ACTIVATION`.
  - Passing to next modules for `module_wait_module` / `module_restart_next`.
  - Error conversion to SERVFAIL, query completion, super notification, and state deletion.
  - Finished-state backtracking to prior modules or final response handling at module 0.
  - Refetch scheduling after answer completion when `need_refetch` is set.

## Response Delivery

- `mesh_query_done` stops serve-expired timers, optionally tries stale cache on SERVFAIL, logs servfail details, generates DNS Error Reporting subqueries when configured, drops stale UDP replies past discard-timeout, logs response-IP/RPZ inform actions, sends replies, runs callbacks, and updates mesh accounting.
- `mesh_send_reply` handles per-client response encoding:
  - Applies RPZ TCP-only truncation for UDP.
  - Converts bogus/failed secure answers to SERVFAIL when validation is required.
  - Reuses a previously encoded response only when EDNS flags/options and alias state are safe to share.
  - Runs inplace callbacks, attaches EDE for validation failures, encodes DNS answers/errors, sends comm replies, updates infra wait-limit, timing histogram, extended stats, and optional reply logs.
- `mesh_do_callback` builds callback responses or callback SERVFAIL/error results and passes security status/reason/ratelimit information.
- `mesh_state_add_reply` deep-copies EDNS options, qname, HTTP/2 stream pointer, and local CNAME alias data into the mesh state region.
- `mesh_state_add_cb` stores callback metadata and EDNS option copies.
- `mesh_state_remove_reply` removes all replies for a comm point, with HTTP/2 stream cleanup and accounting fixes.
- `mesh_remove_callback` removes a matching callback consumer and updates reply/detached counters.

## Serve-Expired and DNS Error Reporting

- `mesh_serve_expired_init` creates per-state serve-expired data and timer.
- `mesh_serve_expired_lookup` performs cache lookup, detects expired TTL, reconstructs `dns_msg`, and rejects bogus/unchecked entries when validation is required.
- `mesh_serve_expired_callback` tries to answer from stale cache, applies response-IP/RPZ logic, follows one alias completion pass, attaches Stale Answer EDE when configured, sends replies/callbacks, and updates expired/RPZ stats.
- `mesh_respond_serve_expired` triggers the same callback path for immediate SERVFAIL fallback.
- `dns_error_reporting` implements RFC9567-style report-query synthesis when EDE and Report-Channel data are available, creating a TXT subquery under `_er...`.

## Cleanup and Stats

- `mesh_state_cleanup` deletes serve-expired timers, drops unsent replies/callbacks with SERVFAIL, removes HTTP/2 backreferences, deinitializes module per-state data, and releases the regional allocator.
- `mesh_state_delete` detaches subqueries, removes list membership, fixes reply/detached counters, removes reverse super refs, deletes from run/all trees, and cleans up the state.
- `mesh_stats`, `mesh_stats_clear`, `mesh_log_list`, and `mesh_get_mem` provide operational accounting and diagnostics.

## Research Notes

- Mesh state is intentionally per-thread; no locks appear in this implementation path.
- Correct accounting is delicate: `num_reply_addrs`, `num_reply_states`, `num_detached_states`, forever/jostle lists, HTTP/2 stream pointers, TCP request info, and infra wait-limit counters are updated across several early-return and cleanup paths.
- Regional allocation means many per-state helper entries are not individually freed; deletion is by qstate region release.
