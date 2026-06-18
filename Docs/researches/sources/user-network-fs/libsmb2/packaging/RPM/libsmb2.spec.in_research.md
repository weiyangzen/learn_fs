<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/libsmb2.spec.in -->
# sources/user-network-fs/libsmb2/packaging/RPM/libsmb2.spec.in

Purpose: RPM spec template for building runtime and development libsmb2 packages.

Important APIs, types, and functions: Defines package metadata, source tarball, Autotools build recipe, install/clean phases, runtime `%files`, `devel` subpackage files, and changelog.

Control flow: RPM prep unpacks the tarball, build phase regenerates Autotools files, optionally uses ccache, runs `%configure`, then `make`; install phase uses `DESTDIR` and removes stale `.old` files.

State and persistence behavior: Persists package metadata and installed artifacts into RPM build roots. No application runtime state.

Dependencies and integration points: Depends on rpmbuild macros, Autotools, libtool, ccache optionally, and the source tree's install targets. Integrates with `makerpms.sh`.

Risks: Spec regenerates build system during package build, which can make builds sensitive to local tool versions. Devel file list is explicit and can drift when public headers change. License text is old-style and may not satisfy modern SPDX conventions.

Test signals: Package-build validation and changelog history are the main signals; no spec-specific automated test here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/packaging/RPM/libsmb2.spec.in -->
