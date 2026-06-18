# sources/test-tools/xfstests-bld/release/snapshot-release

Purpose: assembles release output for all supported appliance architectures. It verifies required artifacts exist and are not newer than their git-version files, checks version consistency across architectures, copies artifacts into `release/out_dir`, and regenerates README.

Important functions: `check_file_exists` aborts on missing required files; `check_file_out_of_date` aborts if an artifact is newer than the version file.

Control flow: for `arm64 i386 amd64`, it checks `selftests/git-versions.$arch`, `fstests-bld/xfstests-$arch.tar.gz`, `test-appliance/root_fs.img.$arch`, and `test-appliance/root_fs.$arch.tar.gz`; compares version files against the first architecture; copies all files to output; runs `gen-README`.

State/persistence: creates/updates files under `release/out_dir`.

Dependencies/integration: depends on completed selftests/build artifacts for all architectures, `cmp`, `cp -p`, and `gen-README`.

Risks: bug in mismatch reporting uses `$f` when setting `b="$(basename $f)"`, but `$f` is not set in that scope. Freshness check direction assumes version files should be newer than artifacts. Missing one architecture blocks release.

Test signals: a dry release with intentionally stale/missing artifacts should abort; successful release should populate all expected out_dir files plus README.
