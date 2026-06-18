
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMCancelPrepareRequest.java

Purpose: Cancels OM prepare mode by deleting the on-disk prepare marker after admin authorization.

Important APIs and types: Extends `OMClientRequest`; uses `CancelPrepareResponse`, `OMCancelPrepareResponse`, `OMPrepareResponse` for error response construction, `PrepareState.cancelPrepare`, `OMAction.UPGRADE_CANCEL`, and `Type.CancelPrepare`.

Control flow: Validation logs the request, builds a response, checks superuser privilege when admin authorization is enabled, creates the cancel response, calls `ozoneManager.getPrepareState().cancelPrepare()`, audits success/failure, and returns an error response on IO failure.

State and persistence behavior: Does not mutate OM DB/cache. It deletes local disk prepare marker state, which controls prepare mode across restarts.

Dependencies and integration points: Integrates upgrade/prepare state with OM admin authorization, audit logging, and response protocol.

Risks: The catch returns `OMPrepareResponse` rather than `OMCancelPrepareResponse` on error, which may be intentional reuse but is a type-specific review point. Tests should cover admin denial, marker deletion, no DB cache update, and audit action.
