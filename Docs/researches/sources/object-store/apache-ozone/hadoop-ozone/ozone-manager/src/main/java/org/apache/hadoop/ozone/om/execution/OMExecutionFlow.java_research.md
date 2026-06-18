# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/execution/OMExecutionFlow.java

Purpose: `OMExecutionFlow` is the entry point for submitting external OM requests into the current execution pipeline. Today it primarily wraps write request pre-execution and Ratis submission, leaving room for future non-Ratis flow control.

Important APIs and types: Constructor accepts `OzoneManager`. `submit(OMRequest omRequest, boolean isWrite)` returns `OMResponse` or throws `ServiceException`. Internally it uses `OMClientRequest`, `OzoneManagerRatisUtils`, `OMPerformanceMetrics`, and `OMAuditLogger`.

Control flow: `submit` delegates to `submitExecutionToRatis`. For writes, it creates an `OMClientRequest`, records preExecute latency, calls `preExecute`, and on preExecute failure logs existing audit state, invokes `handleRequestFailure`, and returns an error response. Then it submits to `ozoneManager.getOmRatisServer().submitRequest(requestToSubmit, isWrite)`. If the response is unsuccessful, it invokes request failure handling.

State and persistence behavior: This class has no durable state. It triggers durable state changes by submitting write requests to OM Ratis and updates performance metrics.

Dependencies and integration points: It sits between RPC handlers and the OM Ratis server, integrating request construction, pre-execute mutation, audit cleanup, metrics, and Ratis submission.

Risks and test signals: Write preExecute exceptions must not leak partial side effects; non-write requests bypass preExecute. Tests should cover write success, preExecute failure audit/failure handling, unsuccessful Ratis response handling, read submission bypassing preExecute, and latency metric updates.
