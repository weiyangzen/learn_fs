# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_network_host.rs

Purpose: emits host-wide network I/O totals and per-interface counters.

Important APIs/types: `HostNetworkStats` with total received/transmitted and `per_interface: Vec<(String,u64,u64)>`. `collect_host_network_metrics` accepts optional labels but scheduler passes `None` because interface counters are host-wide.

Control flow: preallocates two total metrics plus two per interface. Total metrics share `HOST_NETWORK_IO_MD` with `direction=received/transmitted`. Per-interface metrics use `HOST_NETWORK_IO_PER_INTERFACE_MD` with `interface` and `direction`, plus optional labels.

State/persistence: stateless. Network counters come from host collection in `stats_collector`.

Dependencies/integration: called by `collect_system_monitoring_metrics`. The scheduler comment explicitly avoids process labels for interface counters.

Risks: interface names can churn in containerized environments and create new series. Optional labels are powerful but dangerous if used with process-specific labels for host-wide values.

Test signals: test verifies four metrics for one interface and asserts the dedicated `rustfs_system_network_host_` prefix.
