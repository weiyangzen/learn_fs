# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/StubResponder.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/StubResponder.groovy

Purpose: FIFO response registry for SMB packet test stubs. API surface is `register(Class, SMB2Packet)` and `respond(Object)`. Control flow stores packet responses in a `Map<Class, Queue<SMB2Packet>>`; response lookup uses the exact runtime class of the request and returns `poll()` from that class queue.

State and persistence: in-memory mutable map of queues, no persistence and no concurrency control. It integrates with stubbed `Connection.send` implementations in DFS-style tests. Risks: exact-class matching means subclasses/interfaces are not supported; exhausted queues return `null` rather than a custom failure; unregistered classes throw `IllegalArgumentException`. Test signal is helper-level only, but it enables deterministic multi-packet flows.
