# sources/security-integrity/cryfs/old-cpp/cpack/CMakeLists.txt

Purpose: Configures CPack packaging for legacy CryFS, including Linux archive/package generators and Windows WiX installer metadata.

Important APIs and types: Defines `append_build_number`, sets `CPACK_PACKAGE_*`, `CPACK_DEBIAN_*`, `CPACK_RPM_*`, `CPACK_WIX_*`, and includes `CPack`. It calls `get_git_version(GITVERSION_VERSION_STRING)`.

Control flow: For CMake versions below 3.3 it warns and skips package generation. Otherwise it chmods Debian maintainer scripts, sets common package metadata/license/contact, derives the Git version, configures WiX-specific version/GUID/install directory/PATH patch on Windows, or TGZ/DEB/RPM settings on Unix, and registers Debian postinst/postrm control extras.

State and persistence behavior: Mutates maintainer script executable bits in the source tree during configure, writes package configuration into the build system, and later `cpack` emits packages. Windows version may include AppVeyor build number.

Dependencies and integration points: Used by top-level packaging and the Windows CI `cpack -G WIX` step. It integrates with `gitversion`, Debian maintainer scripts, RPM metadata, and WiX patch XML.

Risks: `append_build_number` appears to use `STRIPPED_VERSION_NUMBER` internally rather than its `VERSION_NUMBER` parameter, relying on caller scope behavior. Changing source file permissions at configure time is unusual. Debian packages auto-add an APT source through maintainer scripts, which is a significant install side effect. WiX product GUID is fixed.

Test signals: CPack success for TGZ/DEB/RPM/WIX and Windows MSI upload are the main signals. Package-manager install/purge behavior depends on maintainer scripts.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/cpack/CMakeLists.txt` completely for this pass (72 lines, 3963 bytes).
