# sources/test-tools/xfstests-bld/run-fstests/android-xfstests.sh.in

Purpose: install-time wrapper template for `android-xfstests`. It substitutes `@DIR@`, exports `ANDROID_XFSTESTS_DIR`, and execs the real runner.

Important control flow: `DIR=@DIR@`, `ANDROID_XFSTESTS_DIR=$DIR/run-fstests`, `export`, then `exec $ANDROID_XFSTESTS_DIR/android-xfstests "$@"`.

State/persistence: none directly.

Dependencies/integration: generated wrapper allows user-facing binary location to point at installed library tree.

Risks: the run-fstests Makefile in this subset installs kvm/gce wrappers, not this one; packaging must include it elsewhere if Android support is intended.

Test signals: installed wrapper should find `util/get-config` through the exported directory.
