<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/strace.spec.in -->
## sources/test-tools/strace/strace.spec.in

Purpose: RPM spec template for building, testing, installing, and documenting strace releases across Fedora, RHEL/CentOS, and SUSE-style RPM environments. It carries a large conditional license expression, distro-specific dependencies, build macros, `%check` behavior, file manifest, and upstream changelog.

Important APIs/types/functions: Uses RPM sections and macros (`%prep`, `%build`, `%install`, `%check`, `%files`, `%changelog`, `%configure`, `%make_build`, `%make_install`, `%if`, `%define`, `%global`). Template substitutions include `@PACKAGE_VERSION@`, `@COPYRIGHT_YEAR@`, `@STRACE_MANPAGE_DATE@`, `@SLM_MANPAGE_DATE@`, `@RPM_CHANGELOGTIME@`, and `@PACKAGE_BUGREPORT@`.

Control flow: The spec chooses modern SPDX-rich `License:` metadata for newer Fedora/RHEL family builds, older `LGPL-2.1+ and GPL-2.0+` metadata elsewhere, conditionally adds `Group`, source format, xz support, Bluetooth headers, stacktrace/symbol-demangle dependencies, and SELinux dependencies. `%prep` seeds generated version/date files, `%build` prints environment diagnostics then configures with mpers checking and bundled headers, `%install` installs into `%buildroot` and compresses changelogs, and `%check` runs installed `strace -V` plus the automake test suite except on selected 32-bit cases.

State and persistence: Persists packaging metadata into generated files (`.tarball-version`, `.year`, manpage date files), installs binaries/manpages/docs into the RPM buildroot, and emits test logs for `%check`. It does not maintain runtime state outside RPM build directories.

Dependencies and integration: Integrates autotools outputs, GCC/make, distro RPM macro sets, optional `pkgconfig(bluez)`, elfutils/libdw or binutils, libselinux, kernel headers, and the strace test suite. The `%files` section binds packaging to installed `strace`, `strace-log-merge`, manpages, and documentation.

Risks: The license field is intentionally distro-sensitive and can become stale when bundled kernel headers or generated autotools files change. `%check` depends on kernel behavior, architecture width, and availability of optional test dependencies; failing to skip incompatible 32-bit lanes can cause packaging failures unrelated to source correctness.

Test signals: Useful verification is `rpmbuild` expansion on target distro macros, successful configure/build with `--enable-mpers=check --enable-bundled=yes`, `%check` logs including `tests*/test-suite.log` and `ksysent.gen.log`, and package file-list validation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/strace.spec.in -->
