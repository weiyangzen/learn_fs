# sources/user-network-fs/libsmb2/cmake/Modules/FindLibKrb5.cmake

Purpose: This module locates Kerberos 5 headers and library for optional libsmb2 Kerberos support on Linux.

Important APIs and types: It exposes `LibKrb5_ROOT_DIR`, `LibKrb5_LIBRARY`, `LibKrb5_INCLUDE_DIR`, and `LibKrb5_FOUND`. It uses `find_path`, `find_library`, `find_package_handle_standard_args`, and `mark_as_advanced`.

Control flow: The module first searches for a root directory containing `include/krb5.h`, then searches `${root}/lib` for `krb5` and `${root}/include` for `krb5.h`. It requires both library and include directory through standard package handling.

State and persistence behavior: It only populates CMake variables/cache entries. It does not generate files.

Dependencies and integration points: The root CMake file calls this module on Linux when `ENABLE_LIBKRB5` is enabled, and assigns `LIBKRB5_LIBRARY` to `core_DEPENDS`. `ConfigureChecks.cmake` separately defines `HAVE_LIBKRB5` based on header presence.

Risks: The root file uses `${LIBKRB5_LIBRARY}` while this module defines `LibKrb5_LIBRARY`; depending on CMake variable case behavior, this can produce an empty dependency value. It also finds `krb5` but not necessarily `gssapi_krb5`, while the autotools path links `-lgssapi_krb5`.

Test signals: Configure with Kerberos installed and inspect CMake cache/output for `LibKrb5_FOUND` and the actual link line. Authentication tests using Kerberos are needed to prove the dependency is not just detected but linked correctly.
