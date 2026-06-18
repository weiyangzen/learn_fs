# File Research: sources/virtualization/nbdkit/plugins/ocaml/plugin.h

## Purpose
Provides compatibility and runtime-lock helpers shared by the OCaml plugin C stubs.

## Main Contents
Defines a fallback `caml_alloc_initialized_string()` for older OCaml runtimes, optional debug wrappers around runtime acquire/release, and `ACQUIRE_RUNTIME_FOR_CURRENT_SCOPE()` using a cleanup attribute to release the OCaml runtime automatically at scope exit.

## Dependencies
Uses OCaml version/runtime APIs and requires including code to have access to nbdkit debug symbols if runtime-lock debugging is enabled.

## Risks and Notes
The cleanup-attribute pattern is GCC/Clang-specific. The helper assumes all OCaml-calling wrappers use the macro consistently to keep runtime acquire/release paired.
