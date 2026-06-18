# sources/storage-engines/foundationdb/fdbserver/workloads/DiskFailureInjection.cpp

Purpose: Implements a failure-injection workload and failure-injector factory that sends disk delay and/or bit-flip chaos commands to randomly selected storage workers, then verifies chaos metrics appear.

Important APIs/types/functions: `DiskFailureInjectionWorkload`, `injectDiskDelays`, `injectBitFlips`, templated `diskFailureInjectionClient`, `reSendChaos`, `chaosGetStatus`, `periodicEventBroadcast`, `SetFailureInjection`, `latestEventOnWorkers`, and `FailureInjectorFactory`.

Control flow: Client 0 optionally waits `startDelay`, repeatedly fetches storage workers, chooses unchosen addresses, and sends throttle/corrupt commands until configured counts are met. A parallel broadcaster periodically re-sends commands to chosen workers after restarts and fetches `ChaosMetrics`; verification mode runs until non-zero metrics are found, otherwise execution is bounded by `testDuration`.

State and persistence behavior: No FDB keyspace writes occur. Runtime state is `chosenWorkers`; simulator state may mark `corruptWorkerMap[address]=true`. Worker-side failure injection settings are volatile and are re-broadcast to survive worker restarts.

Dependencies/integration: It extends `FailureInjectionWorkload`, disables `Attrition`, uses worker `setFailureInjection` RPCs, storage worker discovery, worker event logs, simulator policy state, and chaos metrics fields `DiskDelays` and `BitFlips`.

Risks: It currently targets storage workers only. Command futures inside `diskFailureInjectionClient` are not awaited by the caller, so errors are traced asynchronously. If a complete storage list cannot be fetched, chaos selection is skipped. Metric lookup tolerates missing attributes but rethrows other errors.

Test signals: `ChaosDisabled`, `DiskFailureInjectionFailed`, `ResendChaos`, `FoundChaos`, `ChaosCouldNotGetStorages`, and non-zero chaos metric counts.
