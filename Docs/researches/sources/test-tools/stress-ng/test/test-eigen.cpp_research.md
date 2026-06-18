# sources/test-tools/stress-ng/test/test-eigen.cpp

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_EIGEN` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `eigen3/Eigen/Dense`. Local macros: `EIGEN_SUPPORTED`. Defined functions: `main`. Referenced calls/builtins: `eigen_build_test`, `Random`, `inverse`, `determinant`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `eigen_build_test`, `Random`, `inverse`, `determinant`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `eigen3/Eigen/Dense`; a C++ compiler and Eigen headers under `eigen3/Eigen/Dense`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: this is a C++ probe inside a mostly C test directory, so it depends on CXX configuration as well as CC.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_EIGEN`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 75 lines.

- Probe category: external library/header link probe.

- Includes: eigen3/Eigen/Dense.

- Calls/builtins detected: eigen_build_test, Random, inverse, determinant.

- Structs/types detected: size_t.
