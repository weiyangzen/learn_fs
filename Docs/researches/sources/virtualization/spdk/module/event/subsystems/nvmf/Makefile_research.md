# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/Makefile

Builds the event NVMe-oF subsystem library.

Key elements:
- Compiles `nvmf_rpc.c` and `nvmf_tgt.c`.
- Produces `event_nvmf`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Runtime dependencies are declared in `nvmf_tgt.c`.

Research notes:
- This build unit contains both startup RPC configuration and the target lifecycle state machine.
