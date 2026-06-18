# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl03.c

Purpose: `TUNGETFEATURES` feature-bit enumeration for `/dev/net/tun` or Android `/dev/tun`. Source comment intent: Copyright (c) International Business Machines Corp., 2008 Copyright (c) Linux Test Project, 2017-2019 Author: Rusty Russell <rusty@rustcorp.com.au> Ported to LTP: subrata <subrata@linux.vnet.ibm.com> Test ioriginally written for kernel 2.6.27..

Important APIs/types/functions: core calls `SAFE_IOCTL`; local functions `verify_features`; key constants/macros `TUNGETFEATURES`, `IFF_VNET_HDR`, `IFF_MULTI_QUEUE`, `IFF_NAPI`, `IFF_NAPI_FRAGS`, `IFF_NO_CARRIER`; local structs `tst_test`; headers `sys/types.h`, `sys/ioctl.h`, `sys/stat.h`, `fcntl.h`, `errno.h`, `linux/if_tun.h`, `tst_test.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `needs_root, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
