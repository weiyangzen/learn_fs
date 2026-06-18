# File Research: sources/virtualization/spdk/lib/mlx5/mlx5_crypto.c

Implements mlx5 hardware crypto device discovery and AES-XTS data encryption key object management for SPDK's mlx5 integration.

Key entry points:
- `spdk_mlx5_crypto_devs_allow()` configures an optional allowlist of mlx5 device names eligible for crypto use.
- `spdk_mlx5_crypto_devs_get()` returns RDMA contexts for Mellanox/mlx5 devices that support the required crypto capabilities.
- `spdk_mlx5_crypto_devs_release()` frees the returned device context array.
- `spdk_mlx5_device_query_caps()` queries general and crypto HCA capabilities through DEVX.
- `spdk_mlx5_crypto_keytag_create()` creates hardware DEK objects for all eligible devices from a plaintext AES-XTS key.
- `spdk_mlx5_crypto_keytag_destroy()` destroys DEK objects, releases protection domains, and scrubs stored keytag bytes.
- `spdk_mlx5_crypto_get_dek_data()` finds the DEK associated with a protection domain and returns its object ID and tweak mode.

Core mechanics:
- Device discovery starts from `spdk_rdma_cm_get_devices()`, filters by Mellanox vendor ID, optional allowlist, RoCE availability for Ethernet ports, and mlx5 crypto capability bits.
- Unsupported devices are rejected when AES-XTS tweak modes are unavailable or wrapped AES-XTS import is required, because this library only handles plaintext key import.
- Device capabilities are read using `MLX5_CMD_OP_QUERY_HCA_CAP` for general HCA caps and then crypto caps.
- Supported key lengths are AES-XTS 128 and 256 pairs, with or without an 8-byte keytag appended.
- `mlx5_crypto_dek_init()` creates a DEVX `MLX5_OBJ_TYPE_DEK` object bound to a protection domain and securely zeroes the copied key material in the command buffer after object creation.
- Each keytag object owns an array of per-device DEKs so later queue/mkey setup can select the DEK matching its protection domain.
- DEK creation is followed by a query that verifies state is `MLX5_ENCRYPTION_KEY_OBJ_STATE_READY` and opaque metadata remains zero.
- Tweak mode is selected per device, preferring big-endian multi-block tweak support when available, otherwise little-endian.

Important invariants:
- `spdk_mlx5_crypto_keytag_create()` either creates DEKs for every eligible device or destroys all partial state before returning an error.
- `keytag->deks_num` is incremented before each per-device attempt so the destroy path can clean partial allocations.
- A returned DEK data lookup is keyed by exact `ibv_pd *`.
- Keytag bytes are stored only when the input key length includes the 8-byte keytag suffix and are scrubbed on destroy.

Filesystem/block relevance:
- This file enables hardware crypto offload for SPDK data paths on mlx5 devices. It is especially relevant to encrypted block devices and storage transports that need per-device crypto key object IDs.

Notable risks:
- The device allowlist is global mutable state without locking.
- Plaintext key import is intentionally unsupported on devices requiring wrapped import, limiting hardware compatibility.
- The error log string for the 256-bit-with-keytag case contains a typo (`"lye"`), harmless but visible in diagnostics.
