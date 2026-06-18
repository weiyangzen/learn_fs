# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/EventTypes.h

Purpose: Defines a typed metric descriptor for completed get-value latency events.

Important APIs/types/functions: `GetValueCompleteDescriptor` contains `int64_t latency`. The `Descriptor<GetValueCompleteDescriptor>` specialization names the event `"GetValueComplete"` and declares the `latency` field with unit `"ns"` using Flow TDMetric descriptor helpers.

Control flow: `DatabaseContext` owns an `EventMetricHandle<GetValueCompleteDescriptor>` and can emit this descriptor when get-value operations complete. The metric framework uses the descriptor specialization to map the struct field to a named metric event.

State and persistence behavior: No durable state; this is a compile-time descriptor for telemetry shape. Runtime samples are emitted through TDMetric infrastructure.

Dependencies and integration points: Depends on `flow/flow.h` and `flow/TDMetric.h`. Integrated into client read metrics through `DatabaseContext`.

Risks: Renaming the descriptor or field changes telemetry consumers. Unit mismatch would corrupt downstream latency interpretation. Additional fields require descriptor updates.

Test signals: Metric registration/compilation; get-value completion emits latency in nanoseconds; telemetry consumer/schema tests for `"GetValueComplete"`.
