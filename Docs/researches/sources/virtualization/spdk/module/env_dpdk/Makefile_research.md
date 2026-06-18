# File Research: sources/virtualization/spdk/module/env_dpdk/Makefile

Builds the DPDK environment RPC helper library.

Key elements:
- Compiles `env_dpdk_rpc.c`.
- Produces `env_dpdk_rpc`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Links into SPDK module build infrastructure through `spdk.lib.mk`.

Research notes:
- This library exposes runtime diagnostics for DPDK environment memory stats.
