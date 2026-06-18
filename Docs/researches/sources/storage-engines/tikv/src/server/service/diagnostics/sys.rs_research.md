# sources/storage-engines/tikv/src/server/service/diagnostics/sys.rs

Purpose: collects host diagnostics for CPU, memory, disk, network, IO, kernel/sysctl, transparent hugepage, and process state into `ServerInfoItem` protobufs.

Important APIs/types/functions: `NicSnapshot`; `cpu_time_snapshot`; `load_info`; `hardware_info`; `system_info`; `process_info`; CPU/memory/NIC/IO/hardware helper functions.

Control flow: load collection compares previous CPU/NIC/IO snapshots with current values. CPU emits load averages and CPU-time fractions; memory emits virtual/swap totals and percentages; NIC and IO emit deltas for devices present in both snapshots. Hardware collection refreshes CPU/memory/disk info, emits quotas, cores, frequency, vendor, arch, cache info, disks excluding `rootfs`, and NIC flags/MAC/IPs. System collection walks `/proc/sys`, sorts sysctl pairs, and reads transparent hugepage setting when available. Process collection lists processes with commands.

State/persistence: read-only OS inspection via `SYS_INFO`, TiKV sys helpers, `/proc/sys`, `/sys/kernel/mm/transparent_hugepage/enabled`, and pnet interfaces.

Dependencies/integration: called by diagnostics `server_info`; depends on `tikv_util::sys`, `sysinfo`, `walkdir`, `pnet_datalink`, `num_cpus`, and diagnostics protobufs. Risks include divide-by-zero on unusual memory/swap totals, environment-sensitive Linux/procfs behavior, broad procfs walking, and permission variability. Tests cover load, system, process, memory quota, and hardware shapes with docker exclusions.
