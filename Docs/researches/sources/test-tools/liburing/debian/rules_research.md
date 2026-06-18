# sources/test-tools/liburing/debian/rules

## sources/test-tools/liburing/debian/rules

Purpose: Debian package build rules for liburing using debhelper.

Important targets/APIs: default `%: dh $@ --parallel`, `override_dh_auto_configure`, and `override_dh_auto_test`. It includes dpkg defaults/buildtools and sets hardening and CFLAGS maintenance variables.

Control flow: debhelper owns most phases. Configure override passes Debian multiarch install paths, `/usr` prefix, man/data dirs, libdevdir, and `CC`. Test override runs `make runtests` only when `DEB_BUILD_OPTIONS` does not include `nocheck`; the file appends `nocheck`, so tests are skipped by default.

State and persistence: writes normal Debian build artifacts through debhelper and liburing build outputs. No custom persistent state outside package build.

Dependencies/integration: integrates with Debian `dh`, `dpkg` variables, `configure`, top-level Makefile, and package metadata.

Risks: default `DEB_BUILD_OPTIONS += nocheck` suppresses package-time tests unless overridden. Only `CC` is passed, not CXX. Multiarch libdir/libdevdir must align with package file lists.

Test signals: successful `dh_auto_configure`, build, install staging, and optionally `make runtests`.
