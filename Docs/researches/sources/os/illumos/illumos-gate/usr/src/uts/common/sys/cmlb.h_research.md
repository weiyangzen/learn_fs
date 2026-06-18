# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cmlb.h

`cmlb.h` defines the common media label/block interface used by target disk drivers. It exposes geometry and media attribute structures, attach behavior flags, validation flags, target callback ops (`tg_rdwr`, `tg_getinfo`), target command constants, VTOC-dependent minor encoding shifts, and opaque `cmlb_handle_t`.

The exported API allocates/frees handles, attaches/detaches devices, validates/invalidates labels, queries partition and EFI capacity information, handles label ioctls, implements label-aware `prop_op`, reports devid storage block, and handles close behavior. The header documents callback contexts and error returns in detail.
