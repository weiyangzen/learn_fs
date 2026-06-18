# sources/test-tools/stress-ng/test/test-libkmod.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_KMOD` and link flags `-lkmod` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `libkmod.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`, `kmod_list_foreach`. Referenced calls/builtins: `kmod_new`, `kmod_module_new_from_lookup`, `kmod_list_foreach`, `kmod_module_get_module`, `kmod_module_get_name`, `kmod_module_get_initstate`, `kmod_module_get_refcnt`, `kmod_module_unref_list`. Important structs/unions/enums: `kmod_ctx`, `kmod_list`, `kmod_module`.

## Control Flow

Control flow is deliberately linear: helper function(s) `kmod_list_foreach` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `kmod_new`, `kmod_module_new_from_lookup`, `kmod_list_foreach`, `kmod_module_get_module`, `kmod_module_get_name`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `libkmod.h`; linker availability for `-lkmod`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_KMOD`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 53 lines.

- Probe category: external library/header link probe.

- Includes: unistd.h, libkmod.h.

- Calls/builtins detected: kmod_new, kmod_module_new_from_lookup, kmod_list_foreach, kmod_module_get_module, kmod_module_get_name, kmod_module_get_initstate, kmod_module_get_refcnt, kmod_module_unref_list.

- Structs/types detected: struct kmod_ctx, struct kmod_list, struct kmod_module.
