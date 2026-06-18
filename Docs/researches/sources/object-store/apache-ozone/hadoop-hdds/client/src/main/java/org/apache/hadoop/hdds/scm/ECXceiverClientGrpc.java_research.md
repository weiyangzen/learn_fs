# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/ECXceiverClientGrpc.java

Purpose: Erasure-coding-specific gRPC xceiver client. It customizes standalone gRPC behavior for EC write semantics and optional gRPC retry policy.

Important APIs/types/functions: Constructor reads EC retry enable/max settings and sets EC write timeout. `shouldBlockAndWaitAsyncReply` always returns false, allowing async EC write requests to proceed without the base class's write synchronization wait. `createChannel` extends the base Netty channel builder with service-config retry policy when enabled. `createRetryServiceConfig` builds the gRPC retry configuration for `DEADLINE_EXCEEDED`.

Control flow: On channel creation, if retries are enabled, it configures max attempts, backoff settings, retryable status codes, target service name, and enables gRPC retry. Async sends rely on external EC synchronization rather than blocking in the client.

State and persistence behavior: Stores one `enableRetries` boolean and inherited channel/cache state. No persistence.

Dependencies and integration points: Extends `XceiverClientGrpc`, uses Ozone EC gRPC config keys, datanode details, Netty gRPC, and container protobuf requests.

Risks: Disabling async blocking assumes EC write layers correctly order and synchronize requests. Retry service config applies to the whole service and currently retries only deadline exceeded, which may or may not match every EC failure mode. `maxAttempts` is read as int but stored in a `double` map value for gRPC config.

Test signals: Tests should verify nonblocking async behavior, EC timeout selection, retry config shape, and retry disabled/enabled channel builder behavior.
