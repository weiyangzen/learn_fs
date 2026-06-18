# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/SCMThroughputBenchmark.java

Purpose: picocli/ServiceLoader Freon Vapor subcommand `scm-throughput-benchmark` (`stb`) for measuring SCM throughput for block allocation, container allocation, and container-report processing. It creates fake datanodes against a real SCM, forces pipelines and safe mode state where needed, and drives SCM client RPCs.

Important APIs/types/functions: `SCMThroughputBenchmark.call`, `createBenchmark`, `initSCMClients`, `registerFakeDatanodes`, `activatePipelines`, `exitSafeMode`; nested `ThroughputBenchmark`, `BlockBenchmark`, `ContainerBenchmark`, `ReportBenchmark`, and `FakeDatanode`; enum `BenchmarkType`. It uses `StorageContainerDatanodeProtocol`, `StorageContainerLocationProtocol`, and `ScmBlockLocationProtocol`.

Control flow: command options pick a benchmark. Cluster setup creates RPC clients, registers fake datanodes, optionally waits for SCM-created RATIS pipelines and force-opens them, then exits safe mode. The benchmark base queues one runnable per configured thread, starts them in a fixed executor, polls counters, shuts down, and prints throughput. Block and container benchmarks run concurrent allocation loops. Report benchmark first allocates containers, distributes reports among fake datanodes, snapshots SCM Prometheus counters, sends heartbeats, and polls metrics until processed counts reach target.

State/persistence: no durable local state. It mutates SCM state by registering synthetic datanodes, allocating containers/blocks, activating pipelines, and changing safe mode. Fake reports contain synthetic storage and container-replica metadata.

Dependencies/integration: Ozone Freon, picocli, `@MetaInfServices(VaporSubcommand.class)`, Hadoop RPC, SCM HAUtils clients, SCM Prometheus endpoint, Ozone protocol protobufs, Apache HttpClient, and replication options.

Risks: `BenchmarkType.valueOf` is case-sensitive; `ReportBenchmark.prepare` indexes `datanodes.get(i)` for `numThreads`, so `numThreads > numDatanodes` can fail. Metrics parsing assumes a space-delimited Prometheus value. Fixed port/default HTTP bind port assumptions and a 60 second pipeline wait make runs environment-sensitive. Fake datanodes ignore SCM commands and can leave benchmark artifacts in a real SCM.

Test signals: no direct test file in this subset. Useful tests would cover option validation, metric parsing, fake report construction, and `numThreads`/`numDatanodes` bounds.
