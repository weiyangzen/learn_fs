# File Research: sources/virtualization/spdk/module/bdev/ocf/Makefile

This Makefile builds the SPDK `bdev_ocf` library. It includes SPDK common rules, sets shared-object version `8.0`, adds environment OCF include flags, and compiles all `*.c` files in the directory through `C_SRCS = $(shell ls *.c)`.

The module uses the blank SPDK map file and declares a dependency from the produced library to the static `ocfenv` library via `spdk_lib_list_to_static_libs`. Because all local C files are included automatically, adding a `.c` file in this directory changes the build without editing the Makefile.
