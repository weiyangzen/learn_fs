# sources/object-store/rustfs/crates/obs/src/metrics/collectors/resource.rs

Purpose: exposes simple RustFS process resource metrics: CPU percent, resident memory bytes, and uptime seconds.

Important APIs/types: `ResourceStats` and `collect_resource_metrics`. This is a compact process-resource collector separate from richer process/system collectors.

Control flow: returns a fixed three-metric vector using descriptors from `schema::process_resource`. CPU remains `f64`; memory and uptime convert from `u64`.

State/persistence: stateless. The scheduler obtains values through `collect_process_metric_bundle` and emits these at the resource interval.

Dependencies/integration: used by the system monitoring scheduler task when `now >= next_resource_run`, alongside full process metrics from `system_process.rs`.

Risks: CPU percentage is documented as possibly exceeding 100 on multi-core systems; alerts should not assume a 0-100 range. Some metrics overlap conceptually with process-specific schema metrics, so duplicate dashboard panels should use the intended namespace.

Test signals: tests cover normal values, zero/default values, CPU above 100, descriptor-name matches, `report_metrics` compatibility, and default field values.
