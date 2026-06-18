<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/RequestHandler.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/RequestHandler.java

Purpose: Interface defining the OM request-handling contract shared by the server-side translator, non-HA execution, and HA Ratis state machine apply path.

Important APIs/types/functions: Declares `handleReadRequest(OMRequest)`, `validateRequest(OMRequest)`, and `handleWriteRequestImpl(OMRequest, ExecutionContext)`. The default `handleWriteRequest` wraps `handleWriteRequestImpl`, adds the returned `OMClientResponse` to `OzoneManagerDoubleBuffer` at the current term/index, and skips that add for `Type.Prepare`.

Control flow: Implementations provide direct read handling and write validation/cache mutation. Callers use the default method when they also need to enqueue the response for asynchronous metadata persistence. The prepare special case avoids double-buffering because prepare has distinct durability/coordination semantics.

State and persistence behavior: The interface owns no state. Its default method is a persistence integration point: it determines whether a write response is handed to the double buffer for later flush to OM DB.

Dependencies and integration points: Depends on protobuf request/response types, `ExecutionContext`, `OMClientResponse`, `OMException`, and `OzoneManagerDoubleBuffer`. `OzoneManagerRequestHandler` is the concrete implementation in this subset.

Risks: Any implementation that bypasses the default method must replicate double-buffer semantics. The `Prepare` exception is protocol-sensitive and should remain aligned with OM state-machine handling.

Test signals: Tests should check writes are enqueued with the exact Ratis term/index except prepare, and that `validateRequest` rejects malformed requests before they reach Ratis.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/protocolPB/RequestHandler.java -->
