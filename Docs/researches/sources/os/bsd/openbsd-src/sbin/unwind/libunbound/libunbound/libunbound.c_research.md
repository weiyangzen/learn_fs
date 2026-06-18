# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/libunbound/libunbound.c

`libunbound.c` implements the public libunbound API: context creation/deletion, configuration, synchronous resolution, asynchronous resolution, event-based resolution, cancellation, result freeing, error strings, local-zone/data mutation, and version reporting.

Context creation initializes logging, optional Winsock, allocator state, random seed state, locks, module environment, default library config, EDNS known-options/string state, auth zones, module stack, and query rbtree. `ub_ctx_create()` additionally creates query/result pipes; `ub_ctx_create_ub_event()` and `ub_ctx_create_event()` create contexts for caller-owned event loops.

Context deletion handles background worker shutdown, fork/thread edge cases, pipe cleanup, event worker cleanup, module deinit/destartup, cached allocators, local zones, locks, tubes, caches, config, forwards, hints, auth zones, random state, outstanding queries, logfile override state, and Winsock cleanup.

Configuration APIs mutate the pre-finalized config under `cfglock`: generic options, config files, trust anchors, trusted-keys files, debug level/output, async threading mode, forwarders, TLS forwarding, stub zones, `/etc/resolv.conf` import, and hosts-file import. Most return `UB_AFTERFINAL` once resolution has finalized the context.

Resolution paths are split across `ub_resolve()` for foreground synchronous work, `ub_resolve_async()` for pipe-driven background worker requests, and `ub_resolve_event()` for event-loop integration. Async results are read with `ub_process()` or `ub_wait()`, decoded by `process_answer_detail()`, converted into `ub_result`, and delivered with callbacks outside locks. `ub_cancel()` marks threaded/event queries cancelled or sends cancel messages to forked workers.

Local-zone APIs finalize the context if needed, then print zones, add/remove zones, and add/remove local RR data. `ub_resolve_free()` releases every allocation owned by a `ub_result`; `ub_strerror()` maps library error codes; `ub_version()` returns `PACKAGE_VERSION`.
