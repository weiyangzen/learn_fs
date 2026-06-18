## sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink_reg.rs

Purpose: provides RAII registration for reporter `DataSink`s.

Important APIs/types/functions: `DataSinkRegHandle`, `DataSinkId`, `DataSinkReg`, and `DataSinkGuard`. `register` allocates a monotonically increasing id, schedules `Task::DataSinkReg(Register)`, and returns a guard that deregisters on drop.

Control flow: caller registers a boxed sink through the reporter scheduler. If scheduling succeeds, the guard retains the scheduler; if it fails, it logs and returns a guard that does not deregister.

State/persistence: only an atomic process-local id counter and guard-held scheduler. Reporter owns the actual sink map.

Dependencies/integration: used by `SingleTargetDataSink` and `PubSubService`; consumed by `Reporter::handle_data_sink_reg` to start/stop recorder collection based on active sinks.

Risks: registration scheduling failure is non-fatal and produces an inert guard; id counter never reuses ids; deregistration is best-effort during drop and can fail during shutdown.

Test signals: reporter tests directly schedule data-sink registration/deregistration tasks; summary tests exercise guard drop behavior.
