# sources/user-network-fs/nfs-ganesha/src/cmake/modules/sanitize-helpers.cmake

## Purpose

`sanitize-helpers.cmake` implements shared sanitizer support logic: mapping target sources to languages/compilers, probing sanitizer flags per compiler, and appending sanitizer flags to targets safely.

## Important APIs, Types, and Functions

Functions are `sanitizer_lang_of_source(FILE RETURN_VAR)`, `sanitizer_target_compilers(TARGET RETURN_VAR)`, `sanitizer_check_compiler_flag(FLAG LANG VARIABLE)`, `sanitizer_check_compiler_flags(FLAG_CANDIDATES NAME PREFIX)`, and `sanitizer_add_flags(TARGET NAME PREFIX)`.

## Control Flow

`sanitizer_lang_of_source` compares a file extension with enabled language extension lists. `sanitizer_target_compilers` walks a target's `SOURCES`, ignores object-library generator expressions, maps sources to compiler IDs, and returns unique compilers. `sanitizer_check_compiler_flags` iterates enabled languages and candidate flags, uses language-specific CMake flag checks, optionally prepends GNU static sanitizer runtime flags, and caches `<PREFIX>_<COMPILER>_FLAGS`. `sanitizer_add_flags` rejects targets compiled by multiple compilers or with no supported sanitizer flag, then appends sanitizer and blacklist flags to `COMPILE_FLAGS` and sanitizer flags to `LINK_FLAGS`.

## State and Persistence Behavior

The helpers write cache variables for detected compiler flags and mutate target properties. They do not persist files.

## Dependencies and Integration Points

They depend on CMake enabled language metadata, `CheckCCompilerFlag`, `CheckCXXCompilerFlag`, optional `CheckFortranCompilerFlag`, and variables set by component sanitizer modules. `FindSanitizers.cmake` and `Find*San.cmake` modules call into these helpers.

## Risks and Edge Cases

Target source lists containing generated files, generator expressions other than `TARGET_OBJECTS`, or language-less sources can lead to no compiler detection. Mixed compiler targets are rejected, which is safer but may skip valid builds. Appending to legacy `COMPILE_FLAGS`/`LINK_FLAGS` properties can interact poorly with modern target options and generator expressions.

## Test Signals

Create C-only, CXX-only, mixed C/CXX same-compiler, mixed compiler, and object-library targets with sanitizer options enabled. Inspect target properties and verify flag checks are cached per compiler.
