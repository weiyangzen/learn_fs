# sources/storage-engines/tikv/components/resolved_ts/src/advance.rs

Purpose: this file advances resolved timestamps asynchronously. It obtains a conservative minimum timestamp, synchronizes the concurrency manager, confirms raft leadership/quorum for target regions, and schedules resolved-ts advancement back to the endpoint worker.

Important APIs and types:
- `AdvanceTsWorker` owns a PD client, single-thread tokio runtime, scheduler, concurrency manager, steady timer, and cached last PD TSO.
- `advance_ts_for_regions` starts an async advancement cycle and later reschedules `Task::AdvanceResolvedTs` with the updated `LeadershipResolver`.
- `LeadershipResolver` caches TiKV gRPC clients, tracks region read progress, builds per-store `CheckLeaderRequest`s, and determines which regions have quorum-confirmed leadership.
- `resolve_by_raft` is an alternate leadership check path through `CdcHandle::check_leadership`.
- Helpers include `reset_check_leader_request`, `get_min_timeout`, `region_has_quorum`, and `get_tikv_client`.

Control flow:
- `advance_ts_for_regions` waits for PD TSO, caches it, updates the concurrency manager max ts, then lowers `min_ts` to the global minimum in-memory lock ts if necessary.
- The worker calls `leader_resolver.resolve(regions, min_ts, Some(interval))`; valid regions are scheduled as `Task::ResolvedTsAdvanced { regions, ts, ts_source }`.
- It then waits for either the configured interval or an external notify, enforces a minimum timeout delay, and schedules `Task::AdvanceResolvedTs` even when no regions were valid so future cycles continue.
- `LeadershipResolver::resolve` clears previous transient results, performs periodic GC, scans `RegionReadProgressRegistry` for local leader info, and builds remote check-leader requests for peer stores.
- It sends check-leader RPCs concurrently and processes them with `select_all`, so one slow/down TiKV does not block all responses. Regions become valid once responding stores satisfy joint-consensus quorum rules.
- gRPC client lookup uses PD store addresses, security manager channels, gzip compression, and cached clients. Retryable failures remove cached clients.

State and persistence behavior:
- No durable storage is written. State is runtime-only: cached clients, reusable request buffers, progress maps, valid/checking sets, and cached last PD TSO.
- Resolved-ts advancement is persisted/propagated by downstream endpoint/resolver/read-progress code after scheduled tasks run.
- `reset_check_leader_request` actively shrinks oversized reusable request buffers, preventing registry size or earlier large requests from retaining excessive memory.

Dependencies and integration points:
- Depends on PD for TSO and store addresses, `ConcurrencyManager` for max-ts and memory-lock constraints, `RegionReadProgressRegistry` for leader/read-state information, and raftstore `CdcHandle` for raft-based fallback checks.
- Uses `kvproto::tikvpb::TikvClient` `check_leader_async` RPCs and `kvrpcpb::CheckLeaderRequest/Response`.
- Schedules `crate::endpoint::Task` variants for the resolved-ts endpoint.
- Metrics track pending resolved-ts work, request sizes/counts, RPC duration, and client initialization duration.

Risks and edge cases:
- PD TSO errors are ignored for the cycle and default to zero; subsequent cycles retry. A zero or lowered timestamp should not advance beyond safety constraints.
- Leadership confirmation requires local leader info plus remote checks; missing/stale read progress or failed RPCs can delay resolved-ts advancement.
- TiFlash or stores without `check_leader` return `UNIMPLEMENTED`; the code treats this as an empty response.
- Joint consensus quorum handling must count incoming and demoting voters correctly; `region_has_quorum` separately checks both majorities.
- The resolver must be rescheduled even for empty regions, or advancement can stop.

Test signals:
- Tests cover request sizing, sending only requested regions despite a large registry, shrinking oversized request buffers on reuse, zero-region no-RPC behavior, and timeout minimum selection.
