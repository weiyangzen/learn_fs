# sources/storage-engines/foundationdb/fdbserver/tester/include/fdbserver/tester/WorkloadUtils.h

Purpose: Declares tester-wide workload result/spec structures and utility actors used by orchestration and workloads.

Important APIs/types/functions: `DistributedTestResults` holds metrics, successes, failures, and `ok()`. `TestSpec` stores title, phase flags, options, timeouts, database use, consistency-check flags, simulation agent modes, knob overrides, and disabled failure-injection workload names. Declares `runWorkload`, `logMetrics`, `databaseWarmer`, and `testExpectedError`.

Control flow: Constructors initialize defaults based on simulation status: simulated tests default to database clearing and consistency checks, different timeout/ping defaults, and all workload phases. `ok()` requires at least one success and zero failures.

State and persistence behavior: `TestSpec` is an in-memory execution contract. It carries `Standalone` Flow refs and knob overrides but does not persist anything itself.

Dependencies and integration points: Includes native API, simulation policy, knob protective groups, tester interfaces, workload declarations, perf metrics, and simulator. Central to `TestSpecParser`, `test.cpp`, `TesterServer.cpp`, and workload implementations.

Risks: Defaults are environment-sensitive through `g_network->isSimulated()`, so constructing specs before network initialization would be risky. `DistributedTestResults` default constructor leaves integer fields uninitialized until assigned by callers.

Test signals: Widespread compile/runtime coverage through all tester runs. `testExpectedError` is a reusable assertion actor for negative async tests.
