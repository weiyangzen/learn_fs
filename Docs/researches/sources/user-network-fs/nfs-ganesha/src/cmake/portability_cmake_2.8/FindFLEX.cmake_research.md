# sources/user-network-fs/nfs-ganesha/src/cmake/portability_cmake_2.8/FindFLEX.cmake

## Purpose

This portability `FindFLEX.cmake` discovers Flex and defines macros to generate scanner sources and wire scanner/parser dependencies on older CMake versions.

## Important APIs, Types, and Functions

It exports `FLEX_FOUND`, `FLEX_EXECUTABLE`, `FLEX_VERSION`, `FLEX_LIBRARIES`, `FLEX_INCLUDE_DIRS`, and macros `FLEX_TARGET(Name Input Output [COMPILE_FLAGS string])` and `ADD_FLEX_BISON_DEPENDENCY(FlexTarget BisonTarget)`.

## Control Flow

The module finds `flex` or `win_flex`, optional `fl` library, and `FlexLexer.h`. It runs `flex --version` and parses the version. `FLEX_TARGET` validates optional compile flags and creates an `add_custom_command` running Flex with `-o<Output>` from `CMAKE_CURRENT_SOURCE_DIR`. `ADD_FLEX_BISON_DEPENDENCY` sets `OBJECT_DEPENDS` on generated scanner outputs to the Bison-generated header.

## State and Persistence Behavior

Generated scanner source is created in the build tree by custom commands. Per-target variables such as `FLEX_<Name>_OUTPUTS`, `FLEX_<Name>_INPUT`, and `FLEX_<Name>_COMPILE_FLAGS` are set.

## Dependencies and Integration Points

It depends on Flex and local `FindPackageHandleStandardArgs.cmake`. `config_parsing/CMakeLists.txt` uses it to generate `conf_lex.c` with prefix `ganeshun_yy` and adds a dependency on the Bison parser header.

## Risks and Edge Cases

The documented usage string misses a closing parenthesis, but diagnostics still identify the macro. `FLEX_EXECUTABLE_opts` is not explicitly reset at macro start, so repeated invocations could inherit options in some CMake scopes. The optional `fl` library/header variables are not required by package handling.

## Test Signals

Configure with Flex present/missing, generate `conf_lex.c`, and ensure scanner compilation waits for `conf_yacc.h`. Version parsing should be checked with old and new Flex output formats.
