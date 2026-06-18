# sources/test-tools/xfstests-bld/release/gen-README

Purpose: generates `release/out_dir/README` from `README.in` by substituting Debian mirror/distro and inserting git-version metadata, with optional notes for tagged xfstests/blktests local changes.

Important variables: derives `DIR`, `BUILD_DIR`, `REL_DIR`, `OUT_DIR`, `APPLIANCE_DIR`, `MIRROR`, `distro`, `xfstests_rel`, and `blktests_rel`.

Control flow: resolves repository root based on script location, sources appliance `config.custom` if present, reads `xfstests/build-distro` when available, detects release tags pointing at current xfstests/blktests heads, creates output dir, runs `sed` with a read command to include `git-versions.amd64`, then appends local-change URLs for release tags.

State/persistence: writes `release/out_dir/README`.

Dependencies/integration: depends on git repos under `fstests-bld`, release output from snapshot steps, sed, realpath, and appliance config.

Risks: hard-coded `git-versions.amd64` means README version content depends on that architecture file. Unquoted paths in several subshells assume no spaces. Tag detection may produce multiple lines if multiple matching tags exist.

Test signals: generated README should have no placeholders and should include current git-version lines and optional release tag notes.
