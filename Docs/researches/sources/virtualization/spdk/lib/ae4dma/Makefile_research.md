# File Research: sources/virtualization/spdk/lib/ae4dma/Makefile

This Makefile builds the SPDK `ae4dma` library from `ae4dma.c`. It sets `SPDK_ROOT_DIR`, includes the common SPDK make rules, declares shared-object version `2.0`, sets `LIBNAME = ae4dma`, and uses `spdk_ae4dma.map` as the symbol map.

Research notes: this is a minimal library build file. The implementation surface for the library is contained in `ae4dma.c` plus the internal/spec headers.
