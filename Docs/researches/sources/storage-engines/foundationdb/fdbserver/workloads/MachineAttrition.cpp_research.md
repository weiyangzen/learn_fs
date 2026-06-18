# sources/storage-engines/foundationdb/fdbserver/workloads/MachineAttrition.cpp

## Purpose
Primary FoundationDB failure-injection workload for killing, rebooting, replacing, or faulting simulated or real workers/machines/regions during tests.

## Important APIs, types, and functions
`MachineAttritionWorkload` derives from `FailureInjectionWorkload` and is registered both as a workload and failure injector. It defines attrition options for machine/worker counts, leave counts, durations, reboot/delete/fault modes, target locality IDs, replacement, wait-for-version, and fault injection. Helpers include `normalAttritionErrors`, `ignoreSSFailuresForDuration`, `shouldInject`, `initializeForInjection`, `getServers`, `sendRebootRequests`, `noSimMachineKillWorker`, and `machineKillWorker`.

## Control flow
In simulation, enabled client 0 collects server zone localities, shuffles them, and runs `machineKillWorker` until `testDuration`. The worker can kill an entire DC, data hall, all switch clusters, or selected zones/machines with random kill types, optional healthy-zone marking, optional DD storage-failure suppression, replacement reshuffling, and iterative backoff. Outside simulation, it sends reboot requests to matching workers or randomly selected non-tester workers. `killSelf` can throw `please_reboot`.

## State and persistence behavior
The workload mutates process liveness, simulated disks, global switch cluster state, healthy-zone system keys, and possibly suppresses DD reactions to storage failures. It does not write normal user data.

## Dependencies and integration points
Deeply integrates with simulator process info, `FDBSimulationPolicyState`, worker client reboot interfaces, management API healthy-zone keys, fault-injection activation, locality data, and recovery retry behavior.

## Risks and test signals
Risks are intentionally broad: destructive process failure, interaction with extra databases, timing around healthy-zone cleanup, and different semantics in simulation versus no-simulation mode. Expected normal errors are `please_reboot` and `please_reboot_delete`. `check` returns the result of the ignore-SS-failures cleanup future, and traces such as `Assassination`, `WorkerKill`, and `AddingFailureInjection` are the main signals.
