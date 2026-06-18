# sources/test-tools/stress-ng/debian/rules

## Purpose
`debian/rules` is the Debian package build driver for stress-ng.

## Important APIs, Types, And Functions
It is a debhelper makefile. It exports hardening build options, requests dpkg build flags and build tools, includes `/usr/share/dpkg/buildflags.mk` and `buildtools.mk`, overrides `dh_auto_build`, disables `dh_dwz`, and delegates all other targets to `dh`.

## Control Flow
For package builds, debhelper invokes this makefile. The build override exports shell-form dpkg build flags and calls `dh_auto_build`, passing `VERBOSE=1` unless `DEB_BUILD_OPTIONS` contains `terse`. The `override_dh_dwz` target is empty, so DWARF optimization is skipped.

## State And Persistence
It writes normal Debian package build artifacts through debhelper and the upstream build system. No runtime stress-ng state is touched.

## Dependencies And Integration Points
It depends on debhelper, dpkg build flags/tools infrastructure, and the upstream Makefile. Debian autopkgtests in `debian/tests` validate the built package.

## Risks
The `$(shell dpkg-buildflags --export=sh)` expression is expanded by make before the recipe line executes; changes to quoting can affect exported hardening flags. Disabling `dh_dwz` may be intentional to avoid debug-info issues, but it affects package size/debug optimization.

## Test Signals
Debian package build logs should show hardening flags and successful `dh_auto_build`. Autopkgtest scripts provide post-build runtime validation.
