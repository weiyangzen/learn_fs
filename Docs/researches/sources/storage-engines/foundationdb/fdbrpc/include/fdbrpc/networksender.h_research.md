## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/networksender.h

Purpose: Implements the coroutine that serializes a reply future back to a remote `ReplyPromise` endpoint.

Important APIs/types/functions: `networkSender<T>(Uncancellable, Future<T> input, Endpoint endpoint, ExplicitVoid = {})` awaits a future and sends either `ErrorOr<EnsureTable<T>>(value)` or an error to the endpoint via `FlowTransport::sendUnreliable()`.

Control flow: Await input; on success send serialized value. On `never_reply`, return without sending. On other Flow errors, assert the error is not `actor_cancelled` and send serialized error.

State and persistence behavior: No state beyond the awaited future and target endpoint. It sends a network message but does not persist data.

Dependencies and integration points: Depends on `FlowTransport`, Flow coroutines, endpoint serialization, and is invoked when deserializing `ReplyPromise<T>` in `fdbrpc.h`.

Risks: It uses unreliable send for replies; higher-level request semantics must handle missing replies/failures. Actor cancellation is asserted as invalid here. `never_reply` intentionally drops the reply, which callers must use only when that behavior is expected.

Test signals: Successful remote reply delivery, error reply delivery, `never_reply` suppression, actor-cancelled assertion coverage, and serialization table compatibility.
