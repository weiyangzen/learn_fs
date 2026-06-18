# File Research: sources/virtualization/spdk/module/accel/mlx5/accel_mlx5.h

This private module header defines the configuration and control surface shared by the mlx5 accel implementation and its RPC adapter. `struct accel_mlx5_attr` contains QP size, global request count, comma-separated allowed device names, a crypto split-block limit for multi-block hardware, and an `enable_driver` flag for the platform driver sequence-merging path.

It declares `accel_mlx5_get_default_attr()`, `accel_mlx5_enable()`, and asynchronous stats dumping through `accel_mlx5_dump_stats()`. The stats API takes an SPDK JSON writer, a public `spdk_accel_mlx5_dump_state_level`, a completion callback, and caller context. The header intentionally keeps implementation internals opaque while including `spdk/module/accel/mlx5.h` for public enum definitions.
