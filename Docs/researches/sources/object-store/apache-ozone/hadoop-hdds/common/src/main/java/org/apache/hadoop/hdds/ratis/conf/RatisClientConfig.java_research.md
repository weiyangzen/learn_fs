## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/conf/RatisClientConfig.java

Purpose: annotated configuration bean for HDDS Ratis client behavior.

Important APIs/configs: watch replication level, write/watch request timeouts, multilinear random retry policy string, exponential backoff base/max sleep and max retries, fixed retry-limited interval/count, retry policy class name, plus nested `RaftConfig` for Ratis `raft.client.*` max outstanding requests and RPC/watch timeouts.

Control flow/state: mutable fields populated by config injection with getters/setters. Defaults are encoded both in annotations and field initializers for durations/ints where present. The bean is later consumed by retry policy creators and `RatisHelper.createRetryPolicy`; nested `RaftConfig` maps properties copied into `RaftProperties`.

Dependencies: HDDS config annotations, `RatisHelper` prefix, Ratis `RaftClientConfigKeys`, Java `Duration`. Integration points: generated default config XML, Ratis client creation, retry policy behavior, write/watch latency and reliability tuning.

Risks: `retrylimitedRetryInterval` and `retrylimitedMaxRetries` lack explicit field initializers and rely on config object injection to apply annotation defaults; malformed retry policy class names fail at client creation; timeout settings must align with Ratis server timeouts; watch type is raw string. Test signals: config binding defaults, setter overrides, retry policy construction, malformed policy string/class, and nested `RaftConfig` propagation into `RaftProperties`.
