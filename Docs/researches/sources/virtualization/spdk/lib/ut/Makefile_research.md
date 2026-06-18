# File Research: sources/virtualization/spdk/lib/ut/Makefile

This Makefile builds SPDK’s CUnit-based unit-test helper library.

It compiles `ut.c` into library `ut`, sets shared-library version `SO_VER := 4` and `SO_MINOR := 0`, links `-lcunit`, uses `spdk_ut.map`, and includes standard SPDK make fragments.

The library centralizes common unit-test CLI handling and CUnit execution for SPDK test binaries.
