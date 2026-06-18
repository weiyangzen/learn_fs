# File Research: sources/virtualization/spdk/module/accel/mlx5/accel_mlx5_rpc.c

This file exposes JSON-RPC control for the mlx5 accel module. `mlx5_scan_accel_module` is a startup RPC that decodes optional `qp_size`, `num_requests`, `allowed_devs`, `crypto_split_blocks`, and `enable_driver`, overlays them on `accel_mlx5_get_default_attr()`, calls `accel_mlx5_enable()`, and returns boolean success or an error.

The runtime RPC `accel_mlx5_dump_stats` decodes an optional `level` value, defaults to channel-level stats, begins a JSON-RPC result, and calls `accel_mlx5_dump_stats()`. Because stats collection walks SPDK channels asynchronously, it wraps the generated RPC context and JSON writer in `rpc_accel_mlx5_dump_stats_ext`; the completion callback either ends the JSON result or sends an internal error. If the initial dump call fails, the handler emits `null` and closes the result.

The file depends on generated RPC context/free helpers from `spdk_internal/rpc_autogen.h`, keeps all decoded heap fields freed, and registers one startup and one runtime RPC.
