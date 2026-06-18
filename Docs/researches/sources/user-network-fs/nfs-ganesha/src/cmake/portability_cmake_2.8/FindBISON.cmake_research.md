# sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindBISON.cmake

## Purpose

This portability `FindBISON.cmake` provides Bison discovery and a `BISON_TARGET` macro compatible with older CMake 2.8-era environments. NFS-Ganesha uses it to generate the configuration parser from `conf_yacc.y`.

## Important APIs, Types, and Functions

It exports `BISON_EXECUTABLE`, `BISON_VERSION`, `BISON_FOUND`, and macro `BISON_TARGET(Name BisonInput BisonOutput [VERBOSE file] [COMPILE_FLAGS string])`. Internal helper macros are `BISON_TARGET_option_verbose` and `BISON_TARGET_option_extraopts`.

## Control Flow

The module finds `bison` or `win_bison`, runs `--version` with `LC_ALL=C`, parses version strings for GNU Bison and Bison++, and defines `BISON_TARGET` when an executable is available. `BISON_TARGET` validates argument count, handles optional verbose and compile flags, forces `-d`, derives the generated header name by replacing `c` with `h` in the output extension, and creates an `add_custom_command` that runs Bison in `GANESHA_TOP_CMAKE_DIR`.

## State and Persistence Behavior

It creates generated parser source/header outputs in the build tree through custom commands and exposes per-target variables such as `BISON_<Name>_OUTPUTS`, `BISON_<Name>_OUTPUT_HEADER`, and `BISON_<Name>_COMPILE_FLAGS`.

## Dependencies and Integration Points

It depends on Bison and local `FindPackageHandleStandardArgs.cmake`. `config_parsing/CMakeLists.txt` uses `BISON_TARGET(ConfigParser ... COMPILE_FLAGS "--defines -pganesha_yy")`.

## Risks and Edge Cases

Header-name derivation uses a broad `string(REPLACE "c" "h" ...)`, which can alter extensions unexpectedly. Verbose output handling assumes Bison writes `<output-name>.output`. Running in `GANESHA_TOP_CMAKE_DIR` may matter for relative grammar includes.

## Test Signals

Configure with Bison present and absent, generate `conf_yacc.c`/header, and build the config parser. Version parsing should be checked against GNU Bison version formats and Windows `win_bison`.
