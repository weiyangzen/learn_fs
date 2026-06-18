## sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/OzoneClient.java

### Purpose
`OzoneClient` is the closeable client root that binds a `ClientProtocol` proxy, `ConfigurationSource`, and `ObjectStore` facade. It is normally created by `OzoneClientFactory` and gives callers access to object-store operations and the underlying proxy.

### Important APIs and Types
The public constructor accepts `ConfigurationSource` and `ClientProtocol`, creates a new `ObjectStore`, and registers leak tracking through `OzoneClientFactory.track(this)`. Public APIs are `getObjectStore`, `getConfiguration`, `close`, and `getProxy`. A protected testing constructor injects an `ObjectStore` and `ClientProtocol`.

### Control Flow
Construction is straightforward: store the proxy, create the `ObjectStore`, store the configuration, and initialize leak tracking. `close()` closes the proxy and always closes the leak tracker in a `finally` block.

### State and Persistence Behavior
The class owns local references only. It does not persist data itself. Correct lifecycle behavior matters because the proxy owns RPC/network resources and the leak detector reports clients not closed by callers.

### Dependencies and Integration Points
It integrates `ClientProtocol`, `ObjectStore`, `OzoneConfiguration`, and Ratis `UncheckedAutoCloseable`. It is the root type returned by factory methods and used by application code.

### Risks and Edge Cases
If clients do not call `close`, the leak detector should report creation stack traces. If `proxy.close()` throws, leak tracking is still closed. The testing constructor creates a default `OzoneConfiguration`, which may hide configuration-sensitive behavior in tests that use it.

### Test Signals
Tests should verify object-store/proxy identity, close ordering with failing proxy close, leak-tracker close behavior indirectly, and factory-created clients wiring `ObjectStore` to the same proxy.
