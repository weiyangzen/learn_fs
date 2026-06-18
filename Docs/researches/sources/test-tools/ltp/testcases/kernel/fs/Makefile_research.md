# sources/test-tools/ltp/testcases/kernel/fs/Makefile

Purpose: top-level LTP kernel filesystem test Makefile for this subtree. It delegates build/install behavior to the generic trunk target infrastructure.

Important APIs/types/functions: GNU make variables `top_srcdir`, includes `$(top_srcdir)/include/mk/env_pre.mk` and `$(top_srcdir)/include/mk/generic_trunk_target.mk`.

Control flow: the file sets a default `top_srcdir` of `../../..`, imports the LTP environment prelude, then imports the generic trunk target rules. It defines no local targets or source lists.

State/persistence behavior: no runtime state. Build state is produced by the included LTP make fragments.

Dependencies/integration: integrates this directory into the LTP recursive build and install tree. It depends entirely on parent make infrastructure for target discovery.

Risks/test signals: risk is limited to path correctness. If `top_srcdir` is wrong or included make fragments change expectations, filesystem subdirectory recursion may fail.
