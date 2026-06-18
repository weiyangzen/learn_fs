# sources/user-network-fs/samba/source4/torture/local/wscript_build

## Purpose
This Waf build fragment declares the `TORTURE_LOCAL` internal smbtorture module and its broad source/dependency set.

## Important APIs, types, and functions
It computes the embedded Python provision library name, defines `TORTURE_LOCAL_SOURCE` with many utility, auth, registry, LDB, DSDB, FSRVP, NSS, mdspkt, and local test sources, defines `TORTURE_LOCAL_DEPS`, and calls `bld.SAMBA_MODULE('TORTURE_LOCAL', ...)` with init function `torture_local_init`.

## Control flow
At build time, Waf expands the source/dependency strings, generates `proto.h`, and builds the module only when `bld.PYTHON_BUILD_IS_ENABLED()` is true.

## State and persistence behavior
The file does not manage runtime state. It affects persistent build outputs and generated prototypes.

## Dependencies and integration points
This is the build integration point for the local suite registered by `local.c`. Dependencies include NDR/RPC support, crypto, registry, LDB/SAMDB, replacement tests, RPC FSS state, and provision support.

## Risks and edge cases
Python build disablement disables the entire local torture module. Missing sources or dependencies can silently drop coverage or fail compilation/linking. The source list spans multiple directories, making path drift a common maintenance risk.

## Test signals
Successful build exposes the `local` smbtorture suite and all source files included in `TORTURE_LOCAL_SOURCE`.
