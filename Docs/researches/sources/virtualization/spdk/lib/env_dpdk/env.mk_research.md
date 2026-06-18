# File Research: sources/virtualization/spdk/lib/env_dpdk/env.mk

Makefile fragment that computes DPDK include flags, library lists, and linker arguments for SPDK’s DPDK environment.

It locates DPDK include/library directories from config, builds a base DPDK library list, conditionally adds power, crypto, compressdev, vhost, FC/hash, QAT, mlx5, UADK, and optional DPDK power-driver libraries, then sorts/deduplicates them for static or shared linking.

The fragment sets `ENV_CFLAGS`/`ENV_CXXFLAGS` with the DPDK include path and `ALLOW_EXPERIMENTAL_API`, builds shared-library linker args with rpath and no-as-needed handling, builds static linker args with whole-archive handling plus private dependencies, and adds platform/private libraries such as IPSec_MB, bsd, archive, mlx5/ibverbs, numa, dl, or execinfo when required.

It also carries compiler workarounds for newer GCC warnings and `-fcommon` issues in DPDK-related code.
