# File Research: sources/virtualization/spdk/module/event/subsystems/nvmf/nvmf_rpc.c

Implements startup JSON-RPC configuration for the NVMe-oF event target.

Key elements:
- Registers `nvmf_set_max_subsystems`, allowed only once when max is still zero.
- Decodes discovery filter strings such as `match_any`, `transport`, `address`, and `svcid`.
- Decodes and validates `poll_groups_mask` as a subset of the SPDK environment core mask.
- Registers `nvmf_set_config` for admin command passthrough, poll group mask, discovery filter, DHCHAP options, and duplicate host policy.
- Registers `nvmf_set_crdt` for CRDT values.

Dependencies:
- Uses shared globals from `event_nvmf.h`, SPDK cpuset, util, JSON-RPC, and generated RPC decoders.

Research notes:
- All three RPCs are startup RPCs, shaping target behavior before subsystem initialization.
