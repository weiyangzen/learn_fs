## sources/storage-engines/tikv/components/resource_metering/tests/recorder_test.rs

Purpose: integration tests for CPU recorder attribution through real thread-local resource tags and the public `init_recorder` path.

Important APIs/types/functions: `Operation`, `Operations`, `DummyCollector`, and `merge`. Operations model context attach/detach, CPU-heavy work, and sleeping; `DummyCollector` merges collected records by resource group tag bytes.

Control flow: tests start a recorder, register a collector, spawn workload threads with attached resource tags from `ResourceTagFactory`, join them, then wait for collection and compare expected CPU time within drift.

State/persistence: test-only in-memory expected maps and collected maps behind `Arc<Mutex<_>>`. No filesystem or durable state.

Dependencies/integration: uses `resource_metering::{init_recorder, Collector, RawRecords}`, kvproto context resource group tags, and platform thread CPU stats. Tests are gated to Linux/macOS.

Risks: CPU-time tests are timing-sensitive; `MAX_DRIFT` of 200 ms and post-work sleep reduce flakiness but do not eliminate scheduler variance. Unsupported platforms skip the module.

Test signals: covers heavy CPU, sleeping, mixed work, single-thread and multi-thread attribution, context reset behavior, and merge behavior across tags.
