# sources/user-network-fs/samba/source4/torture/drs/wscript_build

## Purpose
This Waf build fragment declares the `TORTURE_DRS` internal smbtorture module. It bundles DRS initialization, DRS helper utilities, DRS unit tests, and DRS RPC torture tests into one module gated by Python build support.

## Important APIs, Types, and Functions
The file uses `bld.SAMBA_MODULE()` with module name `TORTURE_DRS`. The `source` list includes `drs_init.c`, `drs_util.c`, `unit/prefixmap_tests.c`, `unit/schemainfo_tests.c`, `rpc/dssync.c`, and `rpc/msds_intid.c`. It emits `proto.h` through `autoproto`, declares subsystem `smbtorture`, sets `init_function='torture_drs_init'`, marks the module internal, and enables it only when `bld.PYTHON_BUILD_IS_ENABLED()` is true.

## Control Flow
At configure/build time Waf evaluates this Python fragment. If the Python build is enabled, Waf compiles the listed sources, generates prototypes, links them against the declared dependencies, and registers `torture_drs_init` as the module initializer for smbtorture discovery.

## State and Persistence Behavior
The file has no runtime state. Its persistence effect is build-system metadata: changing sources, dependencies, or enablement changes what torture tests are compiled into the Samba build.

## Dependencies and Integration Points
Dependencies include core Samba utility libraries, LDB, Samba error handling, torture framework, DCERPC/NDR DRSUAPI bindings, GENSEC, hostconfig, DSDB module helpers, ASN.1 utilities, SAMDB, credentials, resolve helpers, loadparm resolve support, and `torturemain`. The build fragment is the integration point that makes the DRS unit files visible to the larger smbtorture binary/module set.

## Risks
Missing a dependency here can surface as link failures or latent build-order problems after source changes. Removing a source silently removes tests from the DRS module. The Python-build gate means environments without Python build support will not compile these tests, which matters for coverage expectations.

## Test Signals
The signal is build-time: successful compilation of `TORTURE_DRS`, generated `proto.h`, resolved `torture_drs_init`, and availability of DRS torture suites in smbtorture.
