# sources/test-tools/xfstests-bld/fstests-bld/dbench/autogen.sh

Purpose: regenerates dbench Autoconf files.

Important APIs and functions: shell script invoking `autoheader` then `autoconf`, exiting on the first failure.

Control flow: runs `autoheader || exit 1`, then `autoconf || exit 1`, then exits 0.

State and persistence: regenerates `config.h.in` and `configure` in the dbench directory.

Dependencies and integration: used by developers or build scripts when Autoconf inputs change. `build-all` runs `autoheader; autoconf` directly instead of this wrapper.

Risks: depends on local Autoconf version; generated output can churn across versions.

Test signals: both Autoconf commands complete and generated files are refreshed.
