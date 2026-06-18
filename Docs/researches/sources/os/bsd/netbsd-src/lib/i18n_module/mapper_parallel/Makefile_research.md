# File Research: sources/os/bsd/netbsd-src/lib/i18n_module/mapper_parallel/Makefile

Builds the parallel mapper module. It explicitly sets `SRCS=citrus_mapper_serial.c`.

This is unusual for the directory name and means the parallel module reuses the serial mapper source file under the common module library name.
