# sources/test-tools/xfstests-bld/kernel-build/kbuild.sh.in

Purpose: install-time wrapper template for the `kbuild` script. It resolves the installed library directory via `@DIR@`, exports `KBUILD_DIR`, and execs the real kernel build driver.

Important control flow: assigns `DIR=@DIR@`, `KBUILD_DIR=$DIR/kernel-build`, exports `KBUILD_DIR`, and `exec`s `$KBUILD_DIR/kbuild "$@"`.

State/persistence: none directly; all persistent behavior belongs to `kbuild`.

Dependencies/integration: generated into a user-facing bin path by install rules.

Risks: bad substitution of `@DIR@` or missing executable target breaks installed command.

Test signals: invoking installed `kbuild --get-kbuild-dir` should return the expected library tree.
