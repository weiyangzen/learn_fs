# sources/user-network-fs/libsmb2/cmake/config.h.cmake

Purpose: This is the CMake template for generated `config.h`, mirroring the portability and package macros that C sources expect from autotools builds.

Important APIs and types: It uses CMake `#cmakedefine` directives for header availability, struct feature macros, package metadata, and version metadata. Macros include `HAVE_ARPA_INET_H`, `HAVE_NETINET_TCP_H`, `HAVE_SYS_UIO_H`, `HAVE_LIBKRB5`, `HAVE_SOCKADDR_LEN`, `HAVE_SOCKADDR_STORAGE`, `HAVE_LINGER`, `STDC_HEADERS`, `PACKAGE_*`, and `VERSION`.

Control flow: `ConfigureChecks.cmake` substitutes the template into `${CMAKE_CURRENT_BINARY_DIR}/config.h`; C sources include it when `HAVE_CONFIG_H` is defined.

State and persistence behavior: The generated header becomes build-tree state and controls conditional compilation for network, file, auth, and platform compatibility code.

Dependencies and integration points: This template is tightly coupled to checks in `ConfigureChecks.cmake` and package variables set in the root `CMakeLists.txt`. It also provides compatibility with sources shared between autotools and CMake builds.

Risks: `#cmakedefine HAVE_X "@HAVE_X@"` can define macros with string-like substitution values rather than a simple `1`, depending on CMake behavior and consumers' expectations. Missing parity with `configure.ac` can make CMake builds exercise different conditional paths than autotools builds.

Test signals: Generated `config.h` should be inspected for expected macros on each target, and both CMake and autotools builds should compile the same core files with equivalent feature availability.
