# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/ConnectionSpec.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/smbj/connection/ConnectionSpec.groovy

Purpose: integration-style tests for connection close, negotiation, authentication flags, error propagation, and DFS resolver selection. It builds `SMBClient` with stub transport/authentication, records `SMBEventBus` events, and asserts forced close emits only `ConnectionClosed`, normal close emits `SessionLoggedOff` then `ConnectionClosed`, unsupported negotiation throws `SMBApiException`, tree-connect session expiration is surfaced, authenticated sessions are not guests, and DFS resolver is enabled only when config and negotiated capabilities allow it.

State and persistence: in-memory event list, connection/session state, and config flags. Dependencies include packet processors, stub auth/transport, `SMBEventBus`, `NtStatus`, negotiated capabilities, and `DFSPathResolver`. Risks covered are lifecycle ordering, status-code propagation, and capability-gated resolver wiring.
