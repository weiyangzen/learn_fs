# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/freon/OmBucketTestUtils.java

Purpose: Shared test utility for OM bucket read/write Freon tests, primarily carrying parameter defaults for mixed read/write workloads and assertions on OM lock metrics.

Important APIs, types, and functions: Contains nested `ParameterBuilder` with default volume/bucket path, counts, data/buffer sizes, thread mix, operation counts, bucket args, description, fluent setters, getters, `getExpectedWriteCount`, and `toString`. Public `verifyOMLockMetrics` asserts `OMLockMetrics` read/write waiting and held sample counts are greater than zero.

Control flow: ParameterBuilder setters mutate fields and return `this` for test-case construction. `getExpectedWriteCount` derives write operations from total threads minus read-thread percentage, write count, and write operation count. `verifyOMLockMetrics` reads formatted metric stat strings, logs them, parses the third whitespace-separated token as sample count, and asserts all four lock metric sample counts are positive.

State and persistence behavior: Builder state is in-memory and per instance. `verifyOMLockMetrics` observes metrics accumulated elsewhere in OM lock instrumentation and does not reset them.

Dependencies and integration points: Depends on `BucketArgs` for bucket creation parameters and `OMLockMetrics` for metrics verification. Used by Freon bucket read/write workload tests outside this subset.

Risks: Metric stat parsing is brittle because it assumes token position. Expected write count truncates integer percentage math. Defaults are tuned for tests and may be expensive if reused accidentally.

Test signals: Positive read/write lock waiting and held sample counts indicate the workload exercised OM lock instrumentation.
