# sources/storage-engines/foundationdb/fdbserver/core/RatekeeperLimitReasons.cpp

## Purpose
`RatekeeperLimitReasons.cpp` defines the stable textual names and descriptions for ratekeeper limiting reasons. These arrays are the presentation/telemetry mapping for the `limitReason_t` enum.

## Important APIs, types, and functions
- `limitReasonName[]` maps enum ordinals to compact machine-readable strings.
- `limitReasonDesc[]` maps the same ordinals to human-readable descriptions.
- `limitReasonEnd` exposes `limitReason_t_end` as an integer.
- `static_assert` checks guarantee both arrays stay in sync with the enum count.

## Control flow
There is no dynamic control flow. Initialization is static at process startup.

## State and persistence behavior
No persistence and no mutable runtime state beyond the exported integer. The table content covers workload/read performance, storage and log queue pressure, MVCC memory, readable/durable lag, disk free-space thresholds by absolute and ratio limits, and failure to fetch the storage server list.

## Dependencies and integration points
The file depends only on `fdbserver/core/RatekeeperLimitReasons.h`. Ratekeeper and status/reporting code can use these arrays to convert limit reason enums into trace, status, or metrics strings.

## Risks and edge cases
The main risk is enum/table drift; static assertions catch missing or extra entries at compile time. Renaming entries may affect dashboards or alerting that depend on stable strings.

## Test signals
Compile-time `static_assert` failures are the local test signal. Runtime validation is through emitted ratekeeper status and trace fields using the expected reason names/descriptions.
