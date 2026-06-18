# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerServiceGrpc.java

## Purpose
`OzoneManagerServiceGrpc` exposes Ozone Manager protobuf requests over gRPC for S3 gateway clients. It adapts gRPC calls into the existing OM protobuf translator path that normally expects Hadoop IPC context.

## Important APIs, types, and functions
- Extends generated `OzoneManagerServiceGrpc.OzoneManagerServiceImplBase`.
- Stores an `OzoneManagerProtocolServerSideTranslatorPB`.
- `submitRequest(OMRequest, StreamObserver<OMResponse>)` logs the command type, creates a synthetic Hadoop `Server.Call`, delegates to `omTranslator.submitRequest(NULL_RPC_CONTROLLER, request)`, writes the response, and completes the observer.
- `getClientId()` returns random UUID bytes for the synthetic call context.

## Control flow
Every gRPC request installs a new `Server.Call` in `Server.getCurCall()` before delegation. This supplies retry/client-id metadata needed by OM Ratis request creation. On successful translator return, it calls `onNext` then `onCompleted`. On any thrown `Throwable`, it logs, wraps the cause in `IOException`, and sends `Status.INTERNAL` through `onError`.

## State and persistence behavior
The service has no persisted state. Per-call state is the temporary Hadoop IPC thread-local call and a local `AtomicInteger` used to assign the synthetic call id. Mutations and persistence occur downstream through the translator and OM/Ratis path.

## Dependencies and integration points
It bridges gRPC, generated OM protobuf types, Hadoop IPC classes under `org.apache.hadoop.ipc_`, the server-side translator, and Ratis request construction. `OzoneManager.startGrpcServer()` creates this service inside `GrpcOzoneManagerServer` when the S3G gRPC server is enabled.

## Risks and edge cases
Catching `Throwable` is broad and may hide serious errors. `new IOException(e.getCause())` can lose the top-level exception message and may produce a weak error description when the cause is null. The synthetic `Server.Call` dependency is explicitly marked TODO; changes in Hadoop IPC or Ratis request code can break gRPC handling if the context shape changes. The call count is local to a single request, so every request starts at call id 1.

## Test signals
Tests should verify successful delegation calls `onNext` and `onCompleted`, translator exceptions become gRPC INTERNAL errors, a Hadoop `Server.Call` with non-empty client id is present during translator execution, command type logging does not mutate requests, and Ratis-enabled OM writes succeed through the gRPC path.
