# sources/user-network-fs/nfs-ganesha/src/config_parsing/CMakeLists.txt

## Purpose

This CMake file builds the NFS-Ganesha configuration parser subsystem. It generates Bison and Flex sources, compiles parser support into an object library, and optionally builds a dynamically loaded RADOS URL provider module.

## Important APIs, Types, and Functions

Key build APIs are `BISON_TARGET(ConfigParser ...)`, `FLEX_TARGET(ConfigScanner ...)`, `ADD_FLEX_BISON_DEPENDENCY`, object library `config_parsing`, module library `ganesha_rados_urls`, and `add_sanitizers(...)`.

## Control Flow

Configure finds Bison and Flex, adds `-D__USE_GNU`, generates `conf_yacc.c` and `conf_lex.c` with Ganesha-specific symbol prefixes, and includes source and binary directories so generated headers are visible. It builds `config_parsing` from `analyse.c`, `config_parsing.c`, `conf_url.c`, `analyse.h`, and generated scanner/parser outputs. If LTTng is enabled, it depends on trace header generation. If `RADOS_URLS` is enabled, it builds `ganesha_rados_urls` from `conf_url_rados.c`, links it against `ganesha_nfsd`, system libraries, RADOS libraries, and a no-undefined linker flag, then installs it.

## State and Persistence Behavior

Build state includes generated parser/scanner files in the binary directory, object-library outputs, optional module library, and installed module artifacts. Sanitizer flags and `-fPIC` are applied to targets.

## Dependencies and Integration Points

It depends on local Bison/Flex modules, sanitizer modules, generated LTTng properties when tracing is enabled, RADOS discovery for URL support, and the main `ganesha_nfsd` target for module linkage.

## Risks and Edge Cases

Generated scanner flags specify both `-Pganeshun_yy` and `-olex.yy.c` while CMake names the output `${CMAKE_CURRENT_BINARY_DIR}/conf_lex.c`; compatibility depends on Flex command-line semantics. Linking a module against `ganesha_nfsd` can be sensitive to executable symbol export and platform linker behavior. `config_parsing` is an object library with explicit `-fPIC`, which must remain true for shared/module consumers.

## Test Signals

Clean builds should regenerate scanner/parser sources and compile `config_parsing`. Builds with `RADOS_URLS=ON`, `USE_LTTNG=ON`, and sanitizers enabled validate optional branches. `verif_syntax` or parser unit tests validate generated parser integration.
