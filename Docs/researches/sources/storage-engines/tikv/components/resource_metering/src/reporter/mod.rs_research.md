## sources/storage-engines/tikv/components/resource_metering/src/reporter/mod.rs

Purpose: owns the reporter worker that aggregates raw recorder batches into protobuf `ResourceUsageRecord`s and uploads them to registered data sinks.

Important APIs/types/functions: `Reporter`, `Task`, `ConfigChangeNotifier`, and `init_reporter`. Key methods are `handle_records`, `handle_data_sink_reg`, `upload_grouptag_record`, `upload_region_record`, `upload`, and `reset`.

Control flow: `Task::Records` aggregates by extra tag; when network IO collection is enabled, it also aggregates by region. Timer ticks upload group-tag records and optional region records at `report_receiver_interval`. First registered data sink registers a recorder collector; removing the last data sink drops that collector and pauses recorder sampling.

State/persistence: keeps in-memory `Records`, `RegionRecords`, data sink map, config, and optional `CollectorGuard`. Upload uses `std::mem::take` to reset accumulated records whether sinks succeed or fail.

Dependencies/integration: depends on recorder collector registration, `CollectorImpl`, data sink registration, aggregation helpers, config, kvproto records, worker timers, and metrics/logging through sink implementations.

Risks: upload failures drop current aggregates after logging; a hard limit of 10 sinks rejects excess sinks; config changes replace config wholesale; worker name reuses recorder thread prefix, which can complicate thread-level attribution.

Test signals: inline tests cover interval config, basic upload, multiple sinks, deregistration, and network-enabled region reporting.
