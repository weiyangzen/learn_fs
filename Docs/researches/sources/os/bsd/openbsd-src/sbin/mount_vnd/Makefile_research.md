# File Research: sources/os/bsd/openbsd-src/sbin/mount_vnd/Makefile

This Makefile builds `mount_vnd`, links against `libutil`, installs `mount_vnd.8`, enables extra warning diagnostics, and includes `<bsd.prog.mk>`.

Despite the name, this utility configures a vnd device for an image file; it does not call the generic mount helper infrastructure.
