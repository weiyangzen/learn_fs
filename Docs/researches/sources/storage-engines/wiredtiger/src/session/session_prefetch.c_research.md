# sources/storage-engines/wiredtiger/src/session/session_prefetch.c

## Purpose
Contains the session-level gate for page prefetch. It decides whether a read of a `WT_REF` should trigger prefetch based on session configuration, handle type, queue pressure, page type, special handle state, and observed disk-read history.

## Important APIs, Types, and Functions
- `__wt_session_prefetch_check(session, ref)` returns a boolean and updates skip/success statistics.
- Uses `WT_SESSION_PREFETCH_ENABLED`, `WT_DHANDLE_TYPE_TIERED`, `WT_REF_FLAG_INTERNAL`, `WT_BTREE_SPECIAL_FLAGS`, and `session->pf.prefetch_disk_read_count`.

## Control Flow
The function exits immediately if session prefetch is disabled. It then counts an attempt and rejects tiered handles, a full global prefetch queue, internal sessions, internal pages, special btree handles other than verify, and sessions with fewer than two disk reads. Once all gates pass, it increments success stats and returns true.

## State and Persistence Behavior
No persistent state is changed. Runtime effects are limited to statistics and the decision to enqueue or skip prefetch work elsewhere. It reads the connection prefetch queue count with thread-sanitizer-aware helpers and reads dhandle/btree flags from the active session handle.

## Dependencies and Integration Points
Called from page-read paths before scheduling asynchronous prefetch. Integrated with session configuration in `session_api.c`, connection prefetch queue management, btree special-operation flags, tiered storage restrictions, and statistics counters.

## Risks
Over-permissive gating can waste IO or enqueue work for unsupported objects; over-restrictive gating can eliminate useful prefetch. The threshold of two disk reads is a heuristic. Special-handle handling must stay aligned with verify and other operations that can safely prefetch.

## Test Signals
Tests should cover disabled/enabled sessions, internal-session skip, tiered skip, internal-page skip, queue-full skip, special-handle skip with verify exception, first/second disk-read counters, and successful prefetch attempt stats.
