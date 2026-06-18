<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/rules -->
# sources/sync-backup/git-lfs/debian/rules

## Research

`debian/rules` drives Debian packaging through debhelper and `dh_golang`. It maps Debian architectures to Go `GOARCH`, sets `DH_GOPKG`, vendor excludes, module/vendor flags, `FORCE_LOCALIZE`, `PATH`, and Go cache, then defines overrides for clean, build, strip, golang metadata, install, and tests.

The build flow runs localization generation, `dh_auto_build`, cross-build binary copy fixups, manpage generation, installs `git-lfs` into `debian/git-lfs/usr/bin`, and creates temporary symlinks for tests so `dh_auto_test` sees expected repo paths. Persistent effects are build artifacts, generated man files, package staging files, and temporary symlinks removed after tests. Risks include Debian architecture mapping drift, excluded vendored packages, disabled stripping, cross-build path assumptions, symlink cleanup after failed tests, and reliance on `/tmp/gocache`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/rules -->
