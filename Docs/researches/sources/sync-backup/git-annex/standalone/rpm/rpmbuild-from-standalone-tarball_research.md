<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/rpm/rpmbuild-from-standalone-tarball -->
# sources/sync-backup/git-annex/standalone/rpm/rpmbuild-from-standalone-tarball

Purpose: helper script that builds a `git-annex-standalone` RPM from an existing standalone tarball, without requiring the build host to match the target architecture.

Important control flow: reads `rpmarch`, `tarball`, `version`, and `rpmrepo` from arguments; strips any suffix after the first dash from the version; creates a temp directory with cleanup trap; extracts the tarball there; creates an rpmbuild root; runs `rpmbuild -bb` with `_rpmdir`, `_rpmfilename`, `version`, `release`, and target architecture definitions; then moves the produced `git-annex-standalone.rpm` into `$rpmrepo/git-annex-standalone-$version-$release.$rpmarch.rpm`.

State and persistence: temporary extraction/build root under `mktemp -d`; final RPM written to the requested repository directory. Cleanup removes the temp directory on exit.

Dependencies and integration points: POSIX shell, `tar`, `rpmbuild`, a sibling `git-annex-standalone.spec`, and an existing standalone tarball.

Risks: if required args are missing, it prints usage but does not exit immediately, so subsequent commands can fail less clearly. `cat "$tarball" | tar zx` is less direct than `tar zxf`. It assumes the current directory is a suitable `_rpmdir` for rpmbuild output.

Test signals: build from a fixture tarball for multiple target arches, verify output filename/version, missing-argument behavior, cleanup after failure, and RPM metadata from the spec.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/rpm/rpmbuild-from-standalone-tarball -->
