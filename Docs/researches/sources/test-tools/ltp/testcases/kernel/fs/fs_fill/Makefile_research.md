# sources/test-tools/ltp/testcases/kernel/fs/fs_fill/Makefile

Purpose: build/install metadata for the LTP filesystem test directory `sources/test-tools/ltp/testcases/kernel/fs/fs_fill`. It does not implement runtime test logic; it selects which shell scripts or binaries are installed by the LTP build.

Important APIs/types/functions: GNU make variables `top_srcdir`, `INSTALL_TARGETS`, `MAKE_TARGETS`, `CFLAGS`, and LTP make includes. This file installs `default leaf targets from the LTP make include`; explicit `MAKE_TARGETS` is `not overridden`; extra `CFLAGS` are `-pthread`.

Control flow: make resolves `top_srcdir`, includes `include/mk/testcases.mk, include/mk/generic_leaf_target.mk`, then lets the generic LTP leaf/trunk target rules copy scripts or build C helpers. There are no local recipes.

State/persistence behavior: persistent output is limited to build/install artifacts selected by the generic make framework. The source file itself carries no runtime state.

Dependencies/integration: depends on the surrounding LTP include/mk framework and is consumed by recursive builds from the kernel filesystem testcase tree.

Risks/test signals: failures surface as missing installed tests, missing large-file flags, or an incorrect set of `fs_bind*` scripts. The test signal is build/install success and the presence of the expected target names in the installed testcase directory.
