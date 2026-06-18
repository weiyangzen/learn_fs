# sources/storage-engines/foundationdb/fdbserver/tester/TesterServer.cpp

Purpose: Implements the tester worker service that receives workload recruitment requests, constructs workload objects, executes setup/start/check/metrics phases, monitors database liveness, and handles special urgent consistency-check workloads.

Important APIs/types/functions: `checkAllOptionsConsumed` validates workload option use. `getWorkloadIface` builds a single or compound workload through `IWorkloadFactory`. `printSimulatedTopology` prints grouped simulator process topology. `databaseWarmer`, `pingDatabase`, and `testDatabaseLiveness` keep database liveness checks active. `runWorkloadAsync` serves workload interface requests. `testerServerWorkload` handles normal workload recruitment. `testerServerConsistencyCheckerUrgentWorkload` and helpers handle the one-at-a-time urgent checker path. `testerServerCore` is the long-running recruitment loop.

Control flow: On recruitment, the server validates expected workload title, constructs workload(s), sends back a `WorkloadInterface`, and runs an actor that listens for setup/start/check/metrics/stop requests. Normal workloads are sent into an actor collection. Urgent consistency checker requests bypass normal compound handling and are limited to one active checker per tester, with duplicate/conflicting request detection by `sharedRandomNumber`.

State and persistence behavior: Holds active workload actors, phase result caches (`setupResult`, `startResult`, `checkResult`) to make repeated phase requests idempotent, and one `consistencyCheckerUrgentTester` pair. Database state is mutated by workloads, not by the server wrapper except liveness ping transactions.

Dependencies and integration points: Uses `TesterInterface`, `WorkloadRequest`, `WorkloadInterface`, `WorkloadFactory`, `CompoundWorkload`, `ServerDBInfo`, simulator topology, role tracing, and native database creation. `test.cpp` recruits testers through these interfaces.

Risks: Workload option validation relies on `getOption` blanking consumed values. A workload that forgets to consume options causes `test_specification_invalid`. Normal workload stop is cooperative and not guaranteed to cancel all work immediately. Urgent checker conflict handling intentionally lets a newer checker replace an older one, producing broken promises for the older workload.

Test signals: Trace events include `WorkloadReceived`, `TestBeginAsync`, `TestSetupComplete`, `TestComplete`, `TestCheckComplete`, `WorkloadSendMetrics`, and `ConsistencyCheckUrgent_Tester*`. Liveness failures are severe trace events.
