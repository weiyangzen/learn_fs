# sources/user-network-fs/samba/source4/torture/krb5/wscript_build

## Purpose

`wscript_build` defines the `TORTURE_KRB5` smbtorture module for AD DC builds and selects the correct KDC test source set for Heimdal or MIT Kerberos.

## Important APIs, Types, and Functions

- `bld.CONFIG_SET('AD_DC_BUILD_IS_ENABLED')` gates the module to AD DC builds.
- `bld.CONFIG_SET('SAMBA4_USES_HEIMDAL')` selects Heimdal sources.
- `bld.SAMBA_MODULE('TORTURE_KRB5', ...)` declares the smbtorture module, `torture_krb5_init` init function, `proto.h` autoproto, and dependencies.

## Control Flow

At build configuration time, the script does nothing unless AD DC support is enabled. For Heimdal builds it compiles `kdc-heimdal.c` and `kdc-canon-heimdal.c`; otherwise it compiles `kdc-mit.c` and `kdc-canon-mit.c`. Both variants become an internal module under the `smbtorture` subsystem.

## State and Persistence Behavior

The script creates build graph state only. It does not affect runtime state or generated test data beyond autoproto output.

## Dependencies and Integration Points

The module depends on `authkrb5`, `torture`, and `KERBEROS_UTIL`. It integrates the C test registration entry point into smbtorture and controls which Kerberos provider-specific implementation is compiled.

## Risks and Edge Cases

Build selection must remain synchronized with provider-specific source APIs. Adding a new KDC test to one provider path but not the other can silently diverge test coverage. The non-Heimdal branch indentation is unusual but syntactically valid Python.

## Test Signals

Build success for both Heimdal and MIT configurations is the core signal. Runtime discovery of the `krb5` torture suite and successful execution of provider-specific canonicalization sub-suites confirms module wiring.
