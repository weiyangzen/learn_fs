<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.hpp

Purpose: This header declares the `CPU` utility class used for CPU affinity and topology-aware thread placement.

Important APIs and types: aliases define vectors of pthread IDs and CPU IDs, plus maps from CPU to core and core to CPU set. Static methods count available CPUs, get/set affinity masks, set affinity for a single CPU or CPU set, list CPUs, and build topology maps.

State and integration: the class is stateless. It depends on pthreads, `sched.h`, and platform-specific pthread headers on FreeBSD. It likely integrates with FUSE thread pinning configured by `fuse_cfg.pin_threads`.

Risks and test signals: callers must handle negative errno-style returns from affinity setters/getters. Tests should compile on supported platforms and verify class declarations match the Linux implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.hpp -->
