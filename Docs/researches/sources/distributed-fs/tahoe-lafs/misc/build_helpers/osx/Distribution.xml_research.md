# sources/distributed-fs/tahoe-lafs/misc/build_helpers/osx/Distribution.xml

## Purpose

This macOS installer distribution file describes the product archive created by `productbuild` for Tahoe-LAFS. It defines installer UI metadata, platform checks, component package selection, and license text.

## Important APIs, Types, and Functions

The important XML elements are `<options>`, `<installation-check>`, `<volume-check>`, `<choices-outline>`, `<choice>`, `<pkg-ref>`, and `<license>`. The embedded JavaScript installation check requires `system.sysctl('hw.machine') == 'x86_64'`. The volume check requires macOS 10.7 or newer.

## Control Flow

Installer.app evaluates the architecture check first, validates allowed OS versions, displays a non-customizable single-package install choice, and installs `tahoe-lafs.pkg` as `com.leastauthority.tahoe` with root authorization.

## State, Dependencies, Integration, Risks, and Tests

The XML itself is static packaging metadata. It integrates with `build-osx-pkg.sh` and the package scripts. Risks include a hard-coded `version="1.10.0"` that may diverge from the package build version, x86_64-only assumptions, and stale license text. Tests should run `productbuild`, inspect the produced distribution, and attempt installer validation on supported and unsupported target metadata.
