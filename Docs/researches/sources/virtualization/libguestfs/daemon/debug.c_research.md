# File Research: sources/virtualization/libguestfs/daemon/debug.c

Implements the unstable internal `debug` command surface.

Key points:
- Dispatches subcommands such as `help`, `binaries`, `bmap`, `core_pattern`, `device_speed`, `env`, `error`, `fds`, `ldd`, `ls`, `ll`, `print`, `progress`, `qtrace`, `segv`, `setenv`, `sh`, and `spew`.
- Exposes appliance internals including open fds, environment, executable inventory, ldd output, shell execution outside guest chroot, and file listings.
- Provides test hooks for long errors, progress messages, debug output volume, core dumps, intentional trap crashes, qtrace read patterns, and device speed benchmarking.
- `do_debug_upload` and `do_internal_upload` accept FileIn uploads to arbitrary appliance paths, not guest sysroot paths.
- `do_internal_rhbz914931` is a regression crash path during FileIn receive.
- Not stable ABI; comments explicitly direct users to source for behavior.
