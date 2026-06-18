## sources/storage-engines/tikv/components/resource_metering/src/reporter/collector_impl.rs

Purpose: adapts the recorder-side `Collector` trait into reporter worker tasks.

Important APIs/types/functions: `CollectorImpl::new` and `impl Collector for CollectorImpl`. `collect` wraps incoming `Arc<RawRecords>` in `Task::Records` and schedules it on the reporter scheduler.

Control flow: recorder invokes `collect`; scheduler success hands the batch to `Reporter::handle_records`; scheduler failure increments `IGNORED_DATA_COUNTER` with label `collect` and logs a warning.

State/persistence: stores only a scheduler clone. No durable persistence; dropped batches are not retried.

Dependencies/integration: depends on `tikv_util::worker::Scheduler`, reporter `Task`, `RawRecords`, the resource metering `Collector` trait, and metrics.

Risks: scheduling failure loses an entire raw-record batch. Backpressure is represented only by metric increments and warning logs.

Test signals: reporter tests indirectly exercise this adapter through reporter registration; recorder tests use mock collectors rather than this concrete type.
