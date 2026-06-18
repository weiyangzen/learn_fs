# sources/storage-engines/tikv/components/resource_metering/src/collector.rs

## Purpose
`collector.rs` defines the handoff trait between record-producing code and reporting/scheduling code in resource metering.

## Important APIs, Types, And Functions
`Collector` is a `Send` trait with one method, `collect(&self, records: Arc<RawRecords>)`. It deliberately accepts an `Arc<RawRecords>` so the recorder can pass aggregated data without transferring ownership through a concrete implementation type.

## Control Flow
Recorder-side code collects raw measurements and passes them to registered collectors. Implementations usually schedule reporter work, but the trait itself stays minimal and does not encode scheduling, batching, or upload policy.

## State And Persistence Behavior
The trait owns no state. State lives in implementors and in the `RawRecords` payload.

## Dependencies And Integration Points
It depends only on `Arc` and `crate::RawRecords`. `collector_reg.rs` registers `Box<dyn Collector>` instances with the recorder. Reporter modules implement or consume this trait to bridge to upload pipelines.

## Risks
Because `Collector` is only `Send`, not `Sync`, callers must respect the recorder's scheduling model rather than sharing trait objects arbitrarily. `collect` has no result, so implementations must handle/report failures internally.

## Test Signals
There are no local tests. Registration and recorder integration are exercised through recorder tests and `CollectorRegHandle` behavior.
