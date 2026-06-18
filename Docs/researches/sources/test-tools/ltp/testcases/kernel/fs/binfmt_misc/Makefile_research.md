# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/Makefile

Purpose: LTP Makefile for installing binfmt_misc shell tests and their shared library.

Important APIs/types/functions: `top_srcdir`, `env_pre.mk`, `generic_trunk_target.mk`, and `INSTALL_TARGETS`.

Control flow: sets default `top_srcdir` to `../../../..`, imports the LTP environment prelude, declares `binfmt_misc01.sh`, `binfmt_misc02.sh`, and `binfmt_misc_lib.sh` as install targets, then imports generic trunk target rules.

State/persistence behavior: no runtime state. Build/install state is controlled by LTP make includes.

Dependencies/integration: ties the binfmt_misc tests into LTP installation so scripts are available to the test harness.

Risks/test signals: path and install-list errors would prevent tests from being deployed. The Makefile itself has no executable test signal.
