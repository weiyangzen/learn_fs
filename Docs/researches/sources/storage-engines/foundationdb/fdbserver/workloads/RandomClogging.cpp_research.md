## sources/storage-engines/foundationdb/fdbserver/workloads/RandomClogging.cpp

`RandomCloggingWorkload` is a simulation-only failure injection workload that intermittently clogs network interfaces and pairs of simulator processes. It can run once or iteratively, either with simple random clogs or a "swizzle" mode that clogs a random half of machines with staggered start/end times.

Important APIs are `FailureInjectionWorkload`, `ISimulator::clogInterface`, `ISimulator::clogPair`, `g_simulator->getAllProcesses`, `poisson`, `reportErrors`, and failure-injector registration. `shouldInject` gives eligible database workloads a decreasing random chance of receiving this injection; `initFailureInjectionMode` randomizes scale, clogginess, swizzle mode, and iteration.

`startImpl` runs until `maxRunDuration` or a single `testDuration` depending on `iterate`. `clogClient` repeatedly chooses a random process, computes exponentially distributed clog durations scaled by `scale`, clamps them to remaining workload time, and schedules interface and pair clogs. `swizzleClogClient` chooses many processes, assigns random starts and ends within a clog window, adds extra pair clogs, and schedules delayed interface clogs.

No FDB state is persisted. Runtime state is simulator network impairment. Risks include asynchronous `doClog` futures being launched without awaiting inside the loops, short or zero clogs near workload end, and broad interactions with other failure workloads. It only runs on client 0 in simulation.

Integration points are the simulator fault model and the failure injection factory. Test signals are indirect: the workload returns true from `check`, so value comes from whether the primary workload survives under injected network stalls and whether `reportErrors` catches actor errors.
