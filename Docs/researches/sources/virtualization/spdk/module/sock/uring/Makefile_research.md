# File Research: sources/virtualization/spdk/module/sock/uring/Makefile

Builds the SPDK io_uring socket implementation as library `sock_uring`.

Key contents:
- Sets `SPDK_ROOT_DIR` to the SPDK root relative to `module/sock/uring`.
- Includes `mk/spdk.common.mk`.
- Declares shared object version `SO_VER := 7` and minor `SO_MINOR := 0`.
- Builds `C_SRCS = uring.c`.
- Uses the blank export map `mk/spdk_blank.map`.
- Includes `mk/spdk.lib.mk`.

Role:
- This file is purely build metadata for `uring.c`; it does not include feature gates directly. Runtime registration in `uring.c` probes whether io_uring buffered-ring support is available before registering the implementation.
