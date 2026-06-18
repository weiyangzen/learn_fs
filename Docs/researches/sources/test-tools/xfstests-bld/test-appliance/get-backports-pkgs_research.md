# sources/test-tools/xfstests-bld/test-appliance/get-backports-pkgs

Purpose: cut-down debootstrap-based downloader for Debian backport packages into a target root.

Important flow: set suite to `<arg>-backports`, target to second argument, load debootstrap functions and suite script, read package list from `backport-packages-<suite>`, configure checksum variables, redirect debootstrap logs to `$TARGET/debootstrap/debootstrap.log`, then call `download_indices` and `download`.

State and dependencies: writes `$TARGET/debootstrap` metadata and downloaded deb paths. Depends on installed debootstrap internals, package lists, Debian mirror, `pkgdetails`, and checksums.

Integration points: `gen-image` uses it at stage 5 to download and install backports into the rootfs.

Risks and test signals: tightly coupled to debootstrap implementation and script variables. Missing package list or suite script aborts. Tests should run in a temporary target and verify `debpaths` for expected backport package names.
