# File Research: sources/os/linux/linux-stable/fs/nfs/nfs40.h

## Purpose
Small NFSv4.0-specific internal declaration header.

## Contents
- Client lifecycle and callback recovery:
  - `nfs40_shutdown_client()`
  - `nfs40_init_client()`
  - `nfs40_handle_cb_pathdown()`
- Minor-version ops:
  - `extern const struct nfs4_minor_version_ops nfs_v4_0_minor_ops`
- Server trunking discovery:
  - `nfs40_discover_server_trunking()`

## Research Notes
The implementations are in `nfs40client.c` and `nfs40proc.c`. This header separates v4.0-specific hooks from generic v4 code.
