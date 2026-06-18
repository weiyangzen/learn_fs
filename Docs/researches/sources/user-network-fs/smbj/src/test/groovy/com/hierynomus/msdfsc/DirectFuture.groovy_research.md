# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DirectFuture.groovy
# sources/user-network-fs/smbj/src/test/groovy/com/hierynomus/msdfsc/DirectFuture.groovy

Purpose: tiny test helper implementing `java.util.concurrent.Future<V>` for already-computed SMB packet responses. API surface is constructor `DirectFuture(V contents)`, `get()`, timed `get(long, TimeUnit)`, `isDone()`, `cancel()`, and `isCancelled()`. Control flow is intentionally flat: both `get` methods return stored contents immediately; cancellation always fails and never changes state.

State and persistence: one in-memory `contents` field, no synchronization, no persistence, no timeout behavior. It integrates with DFS/connection stubs that expect `Connection.send` to return a `Future<SMB2Packet>`. Risks are that it cannot model cancellation, blocking, timeout, or exception behavior, so tests using it cover only happy synchronous response paths.
