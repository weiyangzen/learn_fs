# File Research: sources/virtualization/spdk/module/accel/dpdk_cryptodev/accel_dpdk_cryptodev.c

## Purpose

Implements an SPDK accel encryption/decryption backend using DPDK cryptodev PMDs.

## Main Responsibilities

- Registers accel module `"dpdk_cryptodev"` when enabled.
- Supports runtime/startup driver selection among AESNI_MB, QAT, MLX5 PCI, and UADK.
- Initializes DPDK virtual PMDs for AESNI_MB/UADK when selected.
- Discovers/configures cryptodev devices and queue pairs.
- Maintains per-driver qpair assignment for each SPDK IO channel.
- Splits SPDK crypto accel tasks into block-sized DPDK crypto ops.
- Uses LBA-derived IV values, incremented per crypto block.
- Tracks partial submissions, queued tasks, and poller completions.
- Creates and destroys DPDK crypto sessions for SPDK crypto keys.
- Reports cipher support and operation alignment requirements.

## Key Data

- Supported PMD names:
  - `crypto_aesni_mb`
  - `crypto_qat`
  - `mlx5_pci`
  - `crypto_uadk`
- Explicitly skips unsupported `crypto_qat_asym`.
- Supported ciphers:
  - AES-CBC for QAT, UADK, AESNI_MB.
  - AES-XTS for QAT, UADK, AESNI_MB, MLX5 PCI.
- `accel_dpdk_cryptodev_device`: DPDK device metadata and qpair list.
- `accel_dpdk_cryptodev_qp`: queue-pair state, outstanding op count, and QAT spread index.
- `accel_dpdk_cryptodev_key_priv`: selected driver, cipher, optional concatenated XTS key, and per-device key handles.
- `accel_dpdk_cryptodev_task`: SPDK task extension tracking total/submitted/completed crypto ops.
- Global mempools for sessions, mbufs, and crypto ops.

## Supported Operations

- `SPDK_ACCEL_OPC_ENCRYPT`
- `SPDK_ACCEL_OPC_DECRYPT`

## Key Control Flow

- `accel_dpdk_cryptodev_init()` creates vdev if needed, registers mbuf dynamic field, creates mempools, configures all DPDK crypto devices, and registers IO device.
- `_accel_dpdk_cryptodev_create_cb()` assigns one qpair per available driver to the channel and starts the poller.
- `accel_dpdk_cryptodev_submit_tasks()` detects in-place vs out-of-place operation, initializes task counters, and calls `accel_dpdk_cryptodev_process_task()`.
- `accel_dpdk_cryptodev_process_task()` validates key/module ownership, computes block count, caps batch size, allocates mbufs/ops, attaches iov blocks, sets IV and session, enqueues burst, and handles partial enqueue cases.
- `accel_dpdk_cryptodev_poller()` drains qpair completions, frees DPDK resources, completes tasks, and retries queued work.
- `accel_dpdk_cryptodev_key_init()` allocates key-private state, concatenates XTS keys for DPDK, and creates encrypt/decrypt sessions on selected devices.

## Notes / Risks

- One crypto op corresponds to one `block_size` chunk, because IV is based on logical block number.
- QAT qpair selection spreads work using a `32` qpair stride.
- MLX5 keys are bound to a specific device/protection domain, so keys are registered per MLX5 device.
- For QAT, `get_operation_info` requires alignment based on `block_size`.
- Key deinit wipes key handles and XTS concatenated key memory with `spdk_memset_s`.
- `accel_dpdk_cryptodev_fini()` only unregisters if `g_crypto_op_mp` exists; if init did not complete, fini has little to do.
