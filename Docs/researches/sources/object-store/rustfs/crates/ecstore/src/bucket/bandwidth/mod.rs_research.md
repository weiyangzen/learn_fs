# sources/object-store/rustfs/crates/ecstore/src/bucket/bandwidth/mod.rs

Purpose: module declaration file for bucket bandwidth monitoring and throttled reader support.

Important API surface: exports two submodules, `monitor` and `reader`. `monitor` owns throttles, moving average measurements, and reports. `reader` owns `BucketOptions`, `MonitorReaderOptions`, and `MonitoredReader`.

Control flow and state: this file has no runtime control flow or state itself; it defines the namespace boundary used by bucket target replication and read throttling code.

Dependencies and integration points: allows callers to import `crate::bucket::bandwidth::monitor::Monitor` and `crate::bucket::bandwidth::reader::BucketOptions` through a stable module path.

Risks: minimal. Any public API changes in child modules affect users through this module path.

Test signals: no direct tests; child modules contain the functional tests.
