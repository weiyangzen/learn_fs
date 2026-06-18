# sources/storage-engines/foundationdb/flow/include/flow/ChaosMetrics.h

Purpose: declares chaos/fault injection metrics and control singletons for disk, bit-flip, and S3 simulated faults.

Important APIs/types/functions: `ChaosMetrics`, `DiskFailureInjector`, `BitFlipper`, and `S3FaultInjector`.

Control flow: `ChaosMetrics` can clear counters and emit trace fields. `DiskFailureInjector` computes stall/throttle/disk delay from configured intervals and periods. `BitFlipper` stores a bit flip percentage. `S3FaultInjector` stores rates and operation multipliers for S3 errors/throttles/delays/corruptions.

State/persistence: singleton-style injectors hold process-wide chaos configuration. Metrics hold counters and start time.

Dependencies/integration: forward-declared `TraceEvent`; implementations elsewhere connect to simulation and tracing.

Risks: comments note a FIXME to clarify relation to broader simulation chaos. Rates are simple doubles without visible range enforcement in the header. Singleton mutable state needs disciplined reset between tests.

Test signals: trace fields from `ChaosMetrics`, simulation fault injection behavior, and explicit configuration of disk/S3/bit flip settings.
