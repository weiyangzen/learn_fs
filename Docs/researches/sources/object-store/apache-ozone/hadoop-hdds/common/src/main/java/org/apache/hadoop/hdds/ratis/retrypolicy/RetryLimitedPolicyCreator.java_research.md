## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryLimitedPolicyCreator.java

Purpose: alternate retry policy creator that uses a fixed sleep and maximum retry count.

Important API: `create(ConfigurationSource)` reads `RatisClientConfig.getRetrylimitedMaxRetries` and `getRetrylimitedRetryInterval`, converts interval milliseconds to `TimeDuration`, and returns `RetryPolicies.retryUpToMaximumCountWithFixedSleep`.

Control flow/state: stateless, single config-driven policy construction. Dependencies: HDDS config source, Ratis client config, Ratis retry APIs.

Integration points: selectable through `hdds.ratis.client.retry.policy`. Risks: defaults rely on config injection; zero/negative retry interval or count validation is delegated to Ratis or may produce unexpected behavior. Test signals: config binding, fixed sleep/count behavior, invalid interval/count, and selection via `RatisHelper.createRetryPolicy`.
