# sources/test-tools/ltp/testcases/kernel/fs/fs_readonly/Makefile

Purpose: build/install metadata for the read-only bind mount test. It installs `test_robind.sh`, which exercises normal, bind, and read-only bind mounts.

Important APIs/types/functions: `top_srcdir`, `INSTALL_TARGETS := test_robind.sh`, `env_pre.mk`, and `generic_leaf_target.mk`.

Control flow: the Makefile delegates all build and install behavior to the LTP generic leaf rules after declaring the script target.

State/persistence behavior: no runtime state; persistent effect is installing the shell test into the LTP testcase tree.

Dependencies/integration: depends on the LTP make framework. Runtime behavior lives in `test_robind.sh`, which expects a large block device and filesystem mkfs/mount tools.

Risks/test signals: if this Makefile omits the script target, the readonly bind test will not be installed or runnable from LTP. Build success and target installation are the primary signals.
