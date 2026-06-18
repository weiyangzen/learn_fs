## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/ratis/retrypolicy/RetryPolicyCreator.java

Purpose: small extension point for constructing Ratis `RetryPolicy` instances from HDDS configuration.

Important API: single `create(ConfigurationSource)` method. State/control flow: none in the interface. Dependencies: HDDS config source and Ratis retry policy.

Integration points: `RatisHelper.createRetryPolicy` loads implementations by configured class name. Risks: implementations need public no-arg constructors for current reflection path and should validate config values. Test signals: custom implementation loading, type checking, and exception wrapping in `RatisHelper`.
