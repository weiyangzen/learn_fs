# File Research: sources/virtualization/spdk/module/event/subsystems/Makefile

Selects and orders SPDK event subsystem module builds.

Key elements:
- Always includes bdev, accel, scheduler, iscsi, nvmf, scsi, vmd, sock, iobuf, and keyring.
- Adds Linux-only `nbd`, optional Linux `ublk`, optional vhost, optional vfio-user, and optional fsdev.
- Encodes subsystem build dependencies through `DEPDIRS-*`.
- Notes dependency ordering should mirror dependency declarations in C subsystem files.

Dependencies:
- Uses SPDK subdirectory build infrastructure.

Research notes:
- The declared `DEPDIRS-nvmf` omits keyring and sock even though `nvmf_tgt.c` declares those runtime subsystem dependencies.
