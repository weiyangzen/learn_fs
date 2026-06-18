# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmPolicy.hh

Purpose: defines the abstract scheduling policy interface for BWM and the C entry point contract for external policy plugins.

Important APIs/types/functions: pure virtual `Dispatch`, `Done`, `Schedule`, and `Status`; enum `Flow {Incoming, Outgoing}`; `SchedParms` request descriptor; external `XrdBwmPolicyObject(XrdSysLogger *, const char *, const char *)`.

Control flow: `Schedule` handles a new request and returns positive for immediate dispatch, zero for failure, or negative for queued. `Dispatch` blocks until a queued request can run or must fail. `Done` releases active resources or cancels queued requests. `Status` reports queue/active counts.

State and persistence: none in the abstract base, but the contract requires active/queued request identity stability while a handle is live.

Dependencies and integration points: custom policy shared libraries implement this interface and are loaded by `XrdBwmConfig.cc`. `XrdBwmHandle` relies on exact sign semantics and id reuse rules documented here.

Risks: policy implementers must preserve `abs(handle)` identity across negative/positive returns; violations can lose handles or leak resources. Response buffers are caller-owned and size-limited, but the interface trusts implementers to respect `RespSize`.

Test signals: contract tests for custom policies: immediate, queued, failed, dispatch failure, cancellation, active completion, status counts, and response-buffer bounds.
