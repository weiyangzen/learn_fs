# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_ifc.h

Generated-style Mellanox/mlx5 PRM interface header used by SPDK's mlx5 direct-verbs/devx code. It defines command opcodes, status codes, capability modes, and packed bitfield layouts consumed through `DEVX_SET`, `DEVX_GET`, and `DEVX_ADDR_OF`.

Key contents:
- HCA command opcodes for capabilities, QP/CQ/MKEY/PSV/PD/UAR/UMEM, flow steering, scheduling, crypto, and general objects.
- Capability layouts for general HCA, RoCE, flow tables, e-switch, device memory, ODP, QoS, crypto, and HCA cap 2.
- Memory-key layouts: `mlx5_ifc_mkc_bits`, KLM entries, create/destroy MKEY commands, UMR-relevant fields such as `umr_en`, `translations_octword_size`, `bsf_en`, relaxed ordering, crypto enablement, and signature-error fields.
- QP layouts and transitions: `qpc`, `qpc_ext`, create/destroy/query QP, RST2INIT, INIT2RTR, RTR2RTS, RTS2RTS, plus optional masks used by `mlx5_qp.c`.
- Flow steering and packet modification layouts: match specs, STE v0/v1 definitions, flow tables, groups, FTEs, counters, packet reformat contexts, modify-header actions, match definers.
- Crypto/signature support: crypto caps, login object, DEK object, encryption key object, encryption order and AES-XTS constants.
- Other devx objects: scheduling elements, reserved QPNs, PSV, EQ, PD, UAR, UMEM, TIR/TIS/RQ/SQ/RMP/RQT/SRQ/DCT/XRQ, RoCE address, LAG, AV/QP mapping.

Dependencies:
- Assumes `uint8_t` is available, temporarily defines `u8` as `uint8_t`.
- This header itself contains no runtime functions; correctness depends on exact bit offsets matching mlx5 firmware PRM.

Research notes:
- This file is infrastructure for `mlx5_qp.c` and `mlx5_umr.c`; the implementation files rely on these layouts to issue devx commands directly.
- Because the structs encode hardware ABI, ordinary C refactors are high risk. Field names, sizes, and ordering must be preserved.
- Scope relevance is high for virtualization/block storage: it enables SPDK's userspace NVMe/RDMA mlx5 fast path, MKEY/UMR setup, data-integrity signature, and crypto offload.
