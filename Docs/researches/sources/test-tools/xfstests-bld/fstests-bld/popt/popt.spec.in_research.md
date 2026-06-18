# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.spec.in

Purpose: RPM spec template for building and packaging popt. It describes metadata, build requirements, source location, configure/make/install phases, language file handling, package file list, release tracking, and changelog.

Important sections: `%description`, `%prep`, `%build`, `%install`, `%check`, `%track`, `%clean`, `%files`, and `%changelog`. It installs libpopt, `popt.h`, man pages, and `popt.pc`.

Control flow/state: RPM expands macros, unpacks the source, runs `%configure`, builds, stages into `$RPM_BUILD_ROOT`, runs `make check || :`, and packages installed artifacts with generated `popt.lang`. Persistent outputs are RPM binaries/source packages and installed filesystem entries.

Dependencies/integration: depends on RPM macro environment, gettext, autotools install targets, and pkgconfig directory macros. The `%track` stanza appears RPM5-specific and monitors upstream tarball versions.

Risks: `%check` ignores failures, which prevents test failures from blocking packaging. The `License: X Consortium` and old source URL may need validation in modern packaging. Macro overrides for `_libdir` and `_pkgconfigdir` may conflict with distro policies.

Test signals: RPM build logs should confirm `%find_lang`, installed file ownership, and downstream `rpm -ql` paths; `make check` output still matters even though failure is tolerated.
