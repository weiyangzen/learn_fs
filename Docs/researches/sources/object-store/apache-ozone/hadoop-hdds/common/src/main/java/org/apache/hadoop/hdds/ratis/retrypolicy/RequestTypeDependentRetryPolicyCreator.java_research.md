## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RequestTypeDependentRetryPolicyCreator.java

Purpose: builds a Ratis retry policy that varies by request type and exception class.

Important APIs: implements `RetryPolicyCreator.create(ConfigurationSource)`, plus helpers for exponential backoff, exception-dependent policy, and duration conversion.

Control flow: reads `RatisClientConfig`, constructs exponential backoff and multiple-linear-random policies, then builds a `RequestTypeDependentRetryPolicy`. WRITE requests use no retry for not-replicated/group-mismatch/state-machine exceptions, exponential retry for resource unavailable and timeout, and multilinear random default. WATCH requests use the same no-retry and resource-unavailable behavior, but timeout uses no retry. Write/watch request timeouts are also configured.

State/persistence: stateless. Dependencies: HDDS config source and Ratis client config, Ratis retry APIs, Ratis exception classes, protobuf request type cases. Integration points: `RatisHelper.createRetryPolicy` default policy for Raft clients.

Risks: raw `Class[]` and raw loop lose generic type safety; malformed multilinear policy strings fail during client creation; retry semantics affect consistency/latency under slow datanodes; timeouts of zero/negative durations are not validated here. Test signals: exception mapping matrix, write vs watch timeout behavior, malformed multilinear config, and exponential config boundaries.
