<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/debian/rules -->
# sources/sync-backup/git-annex/debian/rules

Purpose: Debian debhelper rules file for building either the normal package path or a `git-annex-standalone` package variant.

Important variables and targets: exports `BUILDER=./Setup`, `BUILDEROPTIONS=-j1` for reproducible builds, `RELEASE_BUILD=1` to use the changelog version, and `ZSH_COMPLETIONS_PATH`. `STANDALONE_BUILD` is computed by grepping `debian/control` for `Package: git-annex-standalone`. The generic `%:` target delegates to `dh $@`.

Standalone control flow: when `STANDALONE_BUILD=1`, `override_dh_auto_build` runs `make linuxstandalone GIT_ANNEX_PACKAGE_INSTALL=1`; `override_dh_auto_install` runs desktop, docs, and completions install targets into `debian/git-annex-standalone`; `override_dh_fixperms` excludes `ld-linux`; `override_dh_strip` suppresses automatic debug symbols; and `override_dh_makeshlibs` disables maintainer scripts/triggers for private bundled libraries.

State and persistence: produces Debian build artifacts under debhelper-managed directories and package staging roots. It does not persist runtime state.

Dependencies and integration points: debhelper, GNU make, git-annex's `Makefile`, Haskell `Setup`, Debian control metadata, and package split definitions in `debian/install`/`debian/links`.

Risks: package behavior hinges on the grep result from `debian/control`, so control file formatting changes can alter the branch. `-j1` improves reproducibility at build-time cost. Standalone builds deliberately bundle private libraries and skip normal shared-library integration.

Test signals: `dpkg-buildpackage` for both control configurations, check reproducible-build diffs, inspect standalone package contents/permissions, and verify no unwanted `ldconfig` trigger or dbgsym package is generated.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/debian/rules -->
