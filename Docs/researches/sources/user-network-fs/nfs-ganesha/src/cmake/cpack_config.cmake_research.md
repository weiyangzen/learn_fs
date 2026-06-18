# sources/user-network-fs/nfs-ganesha/src/cmake/cpack_config.cmake

Purpose: Defines common CPack metadata and source/binary package generator settings for NFS-Ganesha.

Important APIs/types/functions: Sets `CPACK_PACKAGE_NAME`, `CPACK_PACKAGE_VERSION`, `CPACK_PACKAGE_VENDOR`, `CPACK_PACKAGE_DESCRIPTION_SUMMARY`, Debian maintainer, RPM component behavior, ignored component groups, `CPACK_GENERATOR`, `CPACK_SOURCE_GENERATOR`, source ignore patterns, and `CPACK_SOURCE_PACKAGE_FILE_NAME`.

Control flow: Included by top-level packaging configuration before `include(CPack)` so these variables control generated TGZ/source packages and package metadata.

State and persistence behavior: Packaging configuration state only; generated archives are produced by CPack outside this file.

Dependencies and integration points: Uses `GANESHA_VERSION` from the surrounding build. Integrates with CPack Debian/RPM/TGZ generators but sets both binary and source generators to TGZ here.

Risks: Maintainer and package metadata can drift from distro-specific package files. `CPACK_SOURCE_IGNORE_FILES` prepends git-related ignores while preserving prior ignore patterns, so ordering and regex escaping matter.

Test signals: Run `cpack` and source package generation, inspect archive name/version, metadata, and ignored files.
