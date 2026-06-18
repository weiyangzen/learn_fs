# File Research: sources/local-fs/mtd-utils/tests/fs-tests/integrity/Makefile

## Purpose
Build file for the `integck` filesystem integrity test.

## Key Elements
Sets default `CC = gcc`, include paths for common headers and libubi headers, warning/debug/optimization flags, builds local `libubi.a` from `ubi-utils/libubi.c`, links `integck`, and provides a `debug` target with `-O0`, `INTEGCK_DEBUG`, and `-rdynamic`.

## Dependencies
Depends on `../../../ubi-utils/libubi.c`, libubi headers, common include headers, `ar`, and a C compiler.

## Behavior/Risks
Builds a private static libubi copy in the test directory and removes generated objects, `integck`, and `libubi.a` on clean.
