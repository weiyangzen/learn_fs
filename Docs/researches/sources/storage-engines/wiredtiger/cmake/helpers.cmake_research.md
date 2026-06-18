# sources/storage-engines/wiredtiger/cmake/helpers.cmake

## Purpose
`helpers.cmake` provides shared CMake utility functions for dependency evaluation, cache-backed configuration options, third-party library discovery, filelist parsing, and compile-flag manipulation.

## Important APIs, Types, And Functions
Public helper functions are `eval_dependency`, `config_string`, `config_choice`, `config_bool`, `wt_find_library`, `parse_filelist_source`, `add_cmake_flag`, and `replace_compile_options`.

## Control Flow
`eval_dependency` evaluates dependency expressions. `config_string`, `config_choice`, and `config_bool` parse their mini-DSLs, set/unset cache variables, track disabled states, and optionally fail on unmet dependencies. `wt_find_library` tries `find_package`, pkg-config, then raw library/header search and creates `wt::` aliases. `parse_filelist_source` reads `dist/filelist` style entries and filters by selected architecture/platform groups. The flag helpers append or replace whole flags in cache strings.

## State And Persistence Behavior
Most helpers intentionally write to the CMake cache. Disabled-state variables such as `<name>_DISABLED` preserve transitions across reconfigure. `wt_find_library` writes `HAVE_LIB*` internal cache variables and imported target aliases.

## Dependencies And Integration Points
This file is included by build mode, base config, third-party discovery, and source-list generation scripts. It integrates CMake's parser, package discovery, pkg-config, imported targets, and platform options such as `WT_X86`, `WT_LINUX`, and `WT_WIN`.

## Risks
Dependency strings are evaluated as CMake expressions, so malformed or user-controlled expressions can fail configure. Cache persistence can hide changed defaults unless disabled-state logic is correct. `parse_filelist_source` must stay aligned with filelist group names; unsupported arch/OS combinations can silently omit platform files.

## Test Signals
Configure with dependency-enabled and dependency-disabled options, explicit missing-library requests, package/pkg-config/raw library discovery, source filelist filters for every supported arch/OS, and repeated reconfigure after toggling dependencies.
