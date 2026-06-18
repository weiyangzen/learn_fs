# File Research: sources/virtualization/spdk/lib/ut_mock/Makefile

This Makefile builds SPDK’s unit-test mock helper library.

It compiles `mock.c` into library `ut_mock`, sets shared-library version `SO_VER := 8` and `SO_MINOR := 0`, uses the blank SPDK linker map, and includes common library build rules.

The library is meant to be linked by tests that use linker wrapping and the `spdk_internal/mock.h` wrapper infrastructure.
