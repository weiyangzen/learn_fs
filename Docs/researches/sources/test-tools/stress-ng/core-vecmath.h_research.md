# sources/test-tools/stress-ng/core-vecmath.h

## Purpose
`core-vecmath.h` gates vector-math support for compilers and architectures with known vector-code issues.

## Important APIs, Types, And Functions
The header may undefine `HAVE_VECMATH` when Clang is older than 5 or when GCC older than 6 is used on PPC/PPC64. It exports no functions or types.

## Control Flow
Compile-time feature checks either preserve vector math support or force scalar fallback code in including files such as `core-workload.c`.

## State And Persistence
No runtime state or persistent state exists.

## Dependencies And Integration Points
It includes `core-arch.h` for architecture macros and depends on compiler feature definitions. Vector-capable stressors use `HAVE_VECMATH` to select explicit vector types and operations.

## Risks
The guards encode historical compiler behavior. Removing them can reintroduce very slow or broken builds; over-broad guards can hide useful vector coverage on fixed toolchains.

## Test Signals
Cross-compiler builds are the main signal. Runtime `vecmath`, `vecfp`, `vecint`, and workload methods verify that scalar fallbacks and vector paths both compile and run.
