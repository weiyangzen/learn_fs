# sources/object-store/daos/src/engine/tests/drpc_progress_tests.c

Purpose: cmocka unit tests for the dRPC progress loop that polls listener/session fds, accepts sessions, receives calls, spawns handler ULTs, sends bad-call responses, and cleans up dead sessions.

Important APIs and functions: local helpers create `struct drpc_progress_context`, add session nodes, set mock `poll` revents, and assert session presence/removal. The mock `dss_ult_create()` captures scheduling parameters and frees call context ownership on successful spawn. Tests call `drpc_progress()`, `drpc_progress_context_create()`, and `drpc_progress_context_close()`.

Control flow: validation tests reject null context/listener/session/comm. Poll tests cover zero and negative timeouts, timeout return, poll failure, listener accept success/failure, bad message response, valid message dispatch to a system ULT, recv failure cleanup, `-EAGAIN` no-data propagation without close, session `POLLERR`/`POLLHUP` cleanup, ULT creation failure cleanup, and listener error/hangup failures. Context-close tests verify listener and session close counts.

State and persistence: in-memory dRPC contexts and intrusive lists are allocated/freed per test. Mock globals capture poll fds, recv/send buffers, close counts, accepted fds, and ULT arguments. There is no persistence.

Dependencies and integration: depends on dRPC internals, ABT type declarations, DAOS test mocks, and generated dRPC call/response helpers. It validates the engine listener loop's resource ownership rules and error classification.

Risks: the mock `dss_ult_create()` frees call context when spawn succeeds, so tests do not execute the real handler ULT body. Some errors are intentionally swallowed after per-session cleanup, so regressions can hide if only return codes are checked without close/list membership assertions. Poll fd ordering is part of expectations: sessions before listener.

Test signals: suite name `engine_drpc_progress`; key signals include correct poll timeout/fd setup, accepted session inserted, `-DER_TIMEDOUT` on poll timeout, `FAILED_UNMARSHAL_CALL` response for bad payloads, valid calls spawning `DSS_XS_SYS` ULTs with self-freeing handles, and deterministic cleanup behavior for recv, poll, hangup, and ULT failures.
