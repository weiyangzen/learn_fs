<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/e2fsprogs.spec.in -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/e2fsprogs.spec.in

## Purpose
This RPM spec template packages e2fsprogs into the main utilities package, a development package, and a `uuidd` daemon package. Configure substitutes the e2fsprogs package version before RPM build processing.

## Important APIs, Types, and Functions
RPM sections include package metadata, `%description`, `%package devel`, `%package -n uuidd`, `%prep`, `%build`, `%install`, `%clean`, scriptlets `%post`, `%postun`, `%post devel`, `%postun devel`, `%pre -n uuidd`, and `%files` lists. RPM macros define root install directories and use standard macros such as `%configure`, `%find_lang`, `%defattr`, `%doc`, `%attr`, and `%dir`.

## Control Flow
The build runs `%configure --enable-elf-shlibs --enable-nls`, then `make` and `make check`. Install runs `make install install-libs` with root-specific sbindir/libdir overrides, calls `ldconfig -n` in the build root, creates `/var/lib/libuuid`, and collects translations via `%find_lang`. Scriptlets refresh ldconfig, maintain Info directory entries, and create the `uuidd` user/group before installing daemon-owned files.

## State and Persistence
Installed state includes filesystem utilities in root sbin, shared libraries under root libdir, helper tools and headers under standard development paths, man pages, Info docs, pkg-config files, translation catalogs, and `uuidd` state directory `/var/lib/libuuid`. RPM scriptlets modify system user/group databases and Info indexes.

## Dependencies and Integration Points
It integrates with the configured build system, `ldconfig`, `install-info`, `shadow-utils`, `%find_lang`, and RPM ownership/permission handling. It assumes the e2fsprogs make install targets install files matching the explicit `%files` lists.

## Risks
The file list is static and can drift from build outputs, causing RPM unpackaged-file or missing-file failures. Scriptlets assume legacy locations such as `/sbin/install-info` and `/sbin/nologin`. `make check` in `%build` can make RPM builds environment-sensitive. The spec packages static libraries and many shared libraries together, so ABI/layout changes must update multiple file lists.

## Test Signals
Primary signals are successful `rpmbuild -ba` after configure substitution, no unpackaged/missing files, `%find_lang` producing the expected language file, scriptlet linting, and install/erase tests confirming ldconfig, Info, and uuidd user handling.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/e2fsprogs.spec.in -->
