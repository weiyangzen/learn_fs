# sources/sync-backup/kopia/internal/metrics/metrics_timeseries_test.go

Purpose: validates time-series creation for counters and distribution buckets across users, hosts, aggregation modes, and time resolutions.

Important APIs/types/functions: `CreateTimeSeries`, `CounterValue`, `DurationDistributionValue`, `SizeDistributionValue`, `AggregateByHost`, `AggregateAll`, `TimeResolutionByHour`, `TimeResolutionByDay`, `TimeResolutionByMonth`, `TimeSeries`, and helpers `dayOf`/`monthOf`.

Control flow: counter tests construct snapshots with controlled start/end times and values, then assert exact bucket allocation for single-period, multi-period, host aggregation, all aggregation, default daily resolution, and month-length proportional allocation. Distribution tests build ten-day snapshots with bucket counters and assert each daily point receives scaled bucket counts from both snapshots.

State/persistence behavior: all snapshots are in-memory. Tests document proportional allocation semantics and integer truncation outcomes for calendar months.

Dependencies/integration: uses `testlogging.Context` even though time-series creation currently ignores context. Relies on UTC helper timestamps for deterministic expectations.

Risks/test signals: tests do not cover zero-duration snapshots or min/max/sum scaling for distributions. They strongly protect counter splitting and sorted point output.
