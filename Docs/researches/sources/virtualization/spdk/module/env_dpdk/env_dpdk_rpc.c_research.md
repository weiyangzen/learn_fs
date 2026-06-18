# File Research: sources/virtualization/spdk/module/env_dpdk/env_dpdk_rpc.c

Registers a runtime JSON-RPC method to dump DPDK memory statistics.

Key elements:
- `env_dpdk_get_mem_stats` rejects parameters.
- Writes memory stats to `/tmp/spdk_mem_dump.txt`.
- Calls `spdk_env_dpdk_dump_mem_stats()`.
- Returns a JSON object containing the dump filename.

Dependencies:
- SPDK JSON-RPC and DPDK environment wrapper APIs.

Research notes:
- The output path is fixed, so repeated calls overwrite the same file.
