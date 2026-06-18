# File Research: sources/virtualization/spdk/lib/event/app.c

Implements SPDK's application framework lifecycle, option parsing, environment setup, trace setup, RPC bootstrap, signal handling, and shutdown.

Important behavior:
- Defines default app/DPDK/log/trace options and initializes `struct spdk_app_opts` with ABI-size-aware field assignment.
- Parses global SPDK CLI options including config JSON, CPU mask/lcores, hugepage/memory options, PCI allow/block, RPC socket, trace settings, interrupt mode, and NUMA enforcement.
- Initializes the env layer via `spdk_env_init()`, starts reactors, creates the app thread, sets up trace shared memory, and loads JSON startup/runtime configuration.
- Starts or skips the RPC server depending on options, with support for delayed subsystem init via `--wait-for-rpc`.
- Uses `/var/tmp/spdk_cpu_lock_%03d` lock files to prevent multiple SPDK processes from claiming the same cores unless disabled.
- Installs signal handlers for SIGINT/SIGTERM shutdown and ignores SIGPIPE.
- Tracks baseline per-core `/proc/stat` or FreeBSD CPU time counters for later reactor stats.
- Handles `spdk_app_stop()`, subsystem fini, RPC finish, reactor stop, trace cleanup, env cleanup, and log close.

Registered framework RPCs in this file:
- `framework_start_init`
- `framework_wait_init`
- `framework_disable_cpumask_locks`
- `framework_enable_cpumask_locks`

Filesystem/storage relevance: this is the entrypoint lifecycle used by SPDK storage applications before block, NVMe, vhost, or filesystem-device services are initialized.
