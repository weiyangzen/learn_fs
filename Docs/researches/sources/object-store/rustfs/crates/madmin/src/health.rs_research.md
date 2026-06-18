<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/health.rs -->
# sources/object-store/rustfs/crates/madmin/src/health.rs

Purpose: `health.rs` defines madmin health/system-information DTOs and placeholder getter functions for CPU, partition, OS, process, services, config, errors, and memory information.

Important APIs/types/functions: data structs include `NodeCommon`, `Cpu`, `CpuFreqStats`, `Cpus`, `Partition`, `Partitions`, `OsInfo`, `ProcInfo`, `SysService`, `SysServices`, `SysConfig`, `SysErrors`, and `MemInfo`. Getter functions are `get_cpus`, `get_partitions`, `get_os_info`, `get_proc_info`, `get_sys_services`, `get_sys_config`, `get_sys_errors`, and `get_mem_info`; they currently return defaults. `MemInfo` and `NodeCommon.error` use `skip_serializing_if = Option::is_none`, and swap fields use explicit snake-case renames.

Control flow: all getter functions are stubs returning `Default`. Tests instantiate values, serialize/deserialize selected structs, and assert default behavior. There is no system probing yet.

State and persistence behavior: these are plain in-memory DTOs. Many fields are private, so external callers can serialize/deserialize returned values but cannot construct all structs field-by-field outside the module except for public fields like `NodeCommon` and `Cpu`. Optional memory fields are omitted from JSON when absent.

Dependencies and integration points: depends on `serde` and `HashMap`. Peer REST client code references `get_mem_info`-style health payloads, and this crate provides admin-facing health models. Future implementations will likely integrate OS/process/filesystem probing crates or platform APIs.

Risks: placeholder getters returning empty/default values can be mistaken for real health data unless callers know these functions are TODOs. Many struct fields are private, limiting external construction and possibly making public API evolution harder. `Partition.error` is public but other partition details are private. Numeric units are not documented in the structs, which can lead to inconsistent producers. The memory efficiency test only checks rough struct size, not allocation behavior.

Test signals: tests cover defaults, value construction inside the module, JSON skip behavior, getter stubs returning defaults, debug formatting, and approximate memory footprint. Missing tests include real system data collection, cross-platform behavior, and API compatibility snapshots.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/madmin/src/health.rs -->
