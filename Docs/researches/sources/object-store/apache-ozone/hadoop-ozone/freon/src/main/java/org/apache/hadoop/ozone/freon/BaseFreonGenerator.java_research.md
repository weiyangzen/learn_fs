## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/BaseFreonGenerator.java

Purpose: core execution framework for Freon subcommands: common CLI options, threading, metrics, tracing, progress, naming, Ozone client creation, and helper utilities.

Important APIs/types/functions: options include `--number-of-tests`, `--threads`, `--duration`, `--fail-at-end`, and `--prefix`. Key methods are `init`, `runTests`, `runTaskLoop`, `tryNextTask`, `printReport`, `printOption`, `createOmClient`, `createStorageContainerLocationClient`, `findPipelineForTest`, `generateObjectName`, `generateBucketName`, `ensureVolumeAndBucketExist`, `ensureVolumeExists`, digest helpers, `allowEmptyPrefix`, `allowDuration`, `realTimeStatusSupplier`, and `TaskProvider`.

Control flow: subcommands call `init`, then `runTests(provider)`. `init` starts optional Freon HTTP server, sets counters, resolves or randomizes prefix, parses duration, registers shutdown hooks, creates executor/progress bar, and records start time. `runTests` sets the span name, starts fixed-thread runners, waits until count/duration/failure completion, shuts down progress and executor, and throws if failures occurred.

State and persistence behavior: local atomic counters track attempts/success/failure/completion; `ThreadLocal` stores thread sequence IDs. Persistent effects are delegated to task providers. Shutdown hook prints metrics and stops HTTP server.

Dependencies and integration points: parent `Freon` command, Ozone/OM/SCM clients, HA utils, Dropwizard metrics, OpenTelemetry tracing, picocli, Hadoop RPC/security.

Risks: `counter % testNo` is used even for duration mode, so `testNo` must remain positive; failure handling logs and increments counters but only throws at end; thread-local sequence removal in main shutdown does not remove worker locals; shutdown hooks can print reports even during partial initialization.

Test signals: unit tests should cover prefix resolution, duration validation, failure counting, fail-at-end behavior, pipeline selection, and volume/bucket creation idempotence.
