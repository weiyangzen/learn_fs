# sources/test-tools/ltp/testcases/kernel/fs/binfmt_misc/datafiles/Makefile

Purpose: installs data fixtures used by `binfmt_misc02.sh`.

Important APIs/types/functions: `top_srcdir`, `env_pre.mk`, `generic_leaf_target.mk`, `INSTALL_DIR`, and `INSTALL_TARGETS`.

Control flow: sets default `top_srcdir`, includes the LTP environment prelude, declares install directory `testcases/data/binfmt_misc02`, lists `file.extension` and `file.magic` as install targets, then includes generic leaf target rules.

State/persistence behavior: only build/install artifacts under the LTP install tree.

Dependencies/integration: connects magic/extension fixture files to the LTP data root consumed through `$TST_DATAROOT`.

Risks/test signals: if install paths drift, `binfmt_misc02.sh` cannot find fixtures and will fail recognition tests.
