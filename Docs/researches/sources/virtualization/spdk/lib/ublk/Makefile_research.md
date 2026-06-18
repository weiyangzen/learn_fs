# File Research: sources/virtualization/spdk/lib/ublk/Makefile

This Makefile builds SPDK’s Linux ublk integration library.

It compiles `ublk.c` and `ublk_rpc.c` into library `ublk`, sets shared-library version `SO_VER := 5` and `SO_MINOR := 0`, links against `liburing`, uses `spdk_ublk.map`, and includes the standard SPDK common and library make fragments.

The `-luring` dependency reflects that both control-plane and I/O queues are driven through io_uring commands.
