# sources/storage-engines/foundationdb/fdbcli/MaintenanceCommand.cpp

Purpose: Implements `maintenance`, marking one zone as under maintenance for a duration, clearing maintenance, or reporting current maintenance state.

Important APIs/types/functions: `maintenanceCommandActor`, private `printHealthyZone`, exported `setHealthyZone`, `clearHealthyZone`, `maintenanceSpecialKeyRange`, and `ignoreSSFailureSpecialKey`.

Control flow: With no args, `printHealthyZone` reads the maintenance range and prints either global storage-failure DD disable, no ongoing maintenance, or zone/duration remaining. `maintenance off` clears maintenance. `maintenance on <ZONEID> <SECONDS>` parses seconds with `sscanf` requiring full-token consumption and writes the zone key with seconds. Both set/clear helpers reject normal maintenance operations while `IgnoreSSFailures` is present unless explicitly clearing that state for data-distribution enablement.

State and persistence behavior: Persists one special-key range entry under `\xff\xff/management/maintenance/`. A key named `IgnoreSSFailures` represents data distribution disabled for storage-server failures rather than ordinary maintenance. No local state.

Dependencies and integration points: Shared with `DataDistributionCommand.cpp`, status warnings, and data distribution's interpretation of maintenance metadata. Uses special-key writes and retry loops.

Risks: Only one maintenance zone is supported and enforced by assumptions (`ASSERT(res.size() <= 1)`). Seconds are stored as a string/double and displayed as integer seconds; negative or zero durations are not rejected at parse time. Confusion between maintenance mode and `IgnoreSSFailures` can leave DD failure response disabled.

Test signals: Cover report states, on/off, invalid seconds, zero/negative duration policy, rejection when storage-failure DD disable is active, clearing with `clearSSFailureZoneString`, and transaction retry.
