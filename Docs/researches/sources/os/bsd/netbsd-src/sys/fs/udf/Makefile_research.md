# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/Makefile

Read completely: 7 lines.

This kernel include makefile installs UDF public headers under `/usr/include/fs/udf`. The installed headers listed here are `ecma167-udf.h` and `udf_mount.h`.

Important interactions: this makes the on-media ECMA/UDF layout definitions available outside the kernel source tree; the private `udf.h` in this group is not listed for installation here.

Security/reliability notes: no runtime behavior.
