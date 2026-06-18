# sources/object-store/apache-ozone/hadoop-ozone/mini-cluster/src/main/java/org/apache/hadoop/ozone/MiniOzoneClusterImpl.java

Purpose: Concrete implementation of `MiniOzoneCluster` that starts a single in-process SCM, OM, optional datanodes, and extra services for integration tests.

Important APIs/types/functions: Implements readiness waits, SCM/OM/datanode accessors, client creation, SCM location client creation, restart/shutdown/start operations, and service management. Static helpers stop OM/SCM/datanodes/services safely. Nested `Builder` initializes configuration, creates and starts SCM/OM, initializes SCM/OM storage, creates datanodes, configures ports/directories, and builds the cluster.

Control flow, state, and persistence: Build flow sets mini-cluster metrics/cache modes, initializes metadata directory, tunes OM Ratis timeout and SCM client retry, configures safemode minimum datanodes, starts SCM, starts OM, creates datanode services, starts extra services, injects certificate/secret clients, optionally starts datanodes, and prepares the builder for next use. Runtime readiness waits for SCM leadership, healthy datanode count, safemode exit, and open pipelines. Shutdown closes tracked clients, stops services, deletes base dir, shuts caches/metrics, and asserts RocksDB object metrics have no leaks. Persistence lives under per-cluster temp `scm` and `om` subdirectories for data, Ratis, snapshots, HTTP base, and snapshot diff DB.

Dependencies and integration points: Integrates with HDDS SCM, SCM HA utilities, Ratis server initialization, OM storage/security initialization, datanode services, Ozone client factory, metrics system, container/datanode store caches, RocksDB leak detection, GenericTestUtils port/wait utilities, and Ozone/SCM config keys.

Risks: Port allocation and localhost binding are critical; the code explicitly binds SCM servers to `127.0.0.1` to avoid `0.0.0.0` leaking into datanode connection config. Builder reuse depends on `prepareForNextBuild()` and `removeConfiguration()` correctness. Shutdown swallows exceptions after logging, so test failures can hide cleanup issues. There is duplicated `setSecretKeyClient(secretKeyClient)` in build flow, harmless but noisy. Timing-based readiness waits can be flaky under slow machines.

Test signals: This class is primarily tested by being used across integration tests. Internal leak detection (`ManagedRocksObjectMetrics.INSTANCE.assertNoLeaks`) and codec buffer leak detection provide cleanup signals during shutdown.
