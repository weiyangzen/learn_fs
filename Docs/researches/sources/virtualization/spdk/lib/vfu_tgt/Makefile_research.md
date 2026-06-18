# File Research: sources/virtualization/spdk/lib/vfu_tgt/Makefile

This Makefile builds SPDK’s libvfio-user target library.

It sets shared library version `SO_VER := 5` and `SO_MINOR := 0`, builds `tgt_endpoint.c` and `tgt_rpc.c`, includes libvfio-user headers through `VFIO_USER_INCLUDE_DIR`, links against `VFIO_USER_LIBRARY_DIR`, and adds system libraries `-lvfio-user -ljson-c`.

The output library is `vfu_tgt`, with exported symbols controlled by `spdk_vfu_tgt.map`, and compilation uses standard `mk/spdk.lib.mk` rules.
