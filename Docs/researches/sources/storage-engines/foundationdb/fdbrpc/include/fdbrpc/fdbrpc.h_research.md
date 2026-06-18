## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/fdbrpc.h

Purpose: Defines the core fdbrpc request/reply primitives that bind Flow futures, streams, serialization, endpoints, failure monitoring, and transport delivery.

Important APIs/types/functions: `FlowReceiver` owns endpoint registration and peer references. `NetSAV<T>` receives serialized `ErrorOr<EnsureTable<T>>` replies into a Flow single-assignment variable. `ReplyPromise<T>` is the serializable reply endpoint wrapper. `AcknowledgementReceiver`, `NetNotifiedQueueWithAcknowledgements<T>`, and `ReplyPromiseStream<T>` implement streaming replies with sequence checks and byte acknowledgements. `NetNotifiedQueue<T, IsPublic>` receives request streams, optionally verifying public requests. `RequestStream<T, IsPublic>` sends unreliable messages, reliable `getReply()`, unreliable `tryGetReply()`, reply streams, failure-bounded replies, well-known endpoint registration, and serialization.

Control flow: Local endpoints enqueue directly into local Flow queues; remote endpoints serialize through `FlowTransport::sendUnreliable()` or `sendReliable()`. Reply promises serialize as endpoint tokens, and deserialization creates remote promises plus `networkSender()` for returned futures. `tryGetReply()` races the reply future against failure monitor disconnect/failure signals through `waitValueOrSignal()`. Reply streams exchange an acknowledgement endpoint on first message, enforce monotonically increasing sequence numbers, and throttle senders with `onReady()` based on bytes sent minus acknowledged.

State and persistence behavior: Endpoint registrations, peer references, queue contents, byte counters, and SAV reference counts are in-memory transport state. There is no durable persistence, but endpoint tokens are serialized across the network and are protocol-relevant.

Dependencies and integration points: Depends on Flow futures/queues/serialization/task priorities, `FlowTransport`, `FailureMonitor`, `networkSender`, simulator, and generic actors. Almost every fdbrpc interface struct uses `RequestStream`, `ReplyPromise`, or `ReplyPromiseStream`.

Risks: Reference-count ownership is delicate; destructors remove endpoints or peer references and send broken promises for cancelled streams. Public streams require `T::verify()` or fail static assertion. `ReplyPromiseStream::isError()` appears to return `!queue->isError()`, so users should verify semantics. Sequence mismatch or missing acknowledgement endpoints can break streaming. Reliable send cancellation must be paired on every path.

Test signals: Local and remote request/reply, serialization/deserialization of promises and streams, public request verification rejection, failure monitor unauthorized/disconnect paths, reliable send cancellation, stream acknowledgement throttling, sequence mismatch detection, stream cancellation/broken-promise behavior, and task-priority endpoint creation.
