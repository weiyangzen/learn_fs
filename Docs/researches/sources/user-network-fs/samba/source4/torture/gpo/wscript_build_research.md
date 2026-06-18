# sources/user-network-fs/samba/source4/torture/gpo/wscript_build

## Purpose
This Waf build fragment declares the `TORTURE_GPO` internal smbtorture module that compiles and registers Group Policy torture tests.

## Important APIs, Types, and Functions
The file calls `bld.SAMBA_MODULE('TORTURE_GPO', ...)`. It lists `gpo.c` and `apply.c` as sources, targets subsystem `smbtorture`, depends on `torture samba-util-core ldb`, marks the module internal, generates `proto.h`, and sets `init_function='torture_gpo_init'`.

## Control Flow
During build evaluation Waf compiles the two GPO source files, generates prototypes, links the declared dependencies, and records `torture_gpo_init` as the entry point for module registration.

## State and Persistence Behavior
The fragment has no runtime state. Its persistent effect is build metadata controlling whether GPO torture code is compiled into Samba's internal test module set.

## Dependencies and Integration Points
The dependencies reflect the suite's use of the torture framework, core utility helpers, and LDB/SAMDB-adjacent APIs. The generated `proto.h` connects `gpo.c` and `apply.c` declarations.

## Risks
If `apply.c` gains dependencies without updating this fragment, link failures or missing symbols can occur. If `init_function` no longer matches `gpo.c`, the module may build but fail to register tests.

## Test Signals
Build success and smbtorture discovery of `TORTURE_GPO`/`gpo` are the relevant signals.
