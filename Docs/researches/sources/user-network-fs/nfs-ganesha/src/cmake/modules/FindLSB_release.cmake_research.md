# sources/user-network-fs/nfs-ganesha/src/cmake/modules/FindLSB_release.cmake

Purpose: Finds the `lsb_release` executable and captures distribution metadata into CMake variables.

Important APIs/types/functions: Sets `LSB_RELEASE_EXECUTABLE`, `LSB_RELEASE_VERSION_SHORT`, `LSB_RELEASE_ID_SHORT`, `LSB_RELEASE_DESCRIPTION_SHORT`, `LSB_RELEASE_RELEASE_SHORT`, and `LSB_RELEASE_CODENAME_SHORT`; strips quotes from description; uses standard package handling.

Control flow: If executable is found, runs `lsb_release` with `-vs`, `-is`, `-ds`, `-rs`, and `-cs` and stores stripped outputs. Package success requires only the executable.

State and persistence behavior: Configure-time detection variables only.

Dependencies and integration points: Packaging or distro-specific configuration can consume release metadata.

Risks: Execute results are not checked individually, so command failures can leave empty metadata while the package is considered found. Non-LSB systems may lack the command despite having `/etc/os-release`.

Test signals: Configure on Debian/RHEL/Ubuntu, container images without `lsb_release`, and systems with quoted descriptions.
