<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/wscript_build -->
# sources/user-network-fs/samba/source4/utils/oLschema2ldif/wscript_build

## Purpose

This Waf fragment builds the `oLschema2ldif` converter library, command-line binary, and local cmocka test binary.

## Important APIs, Types, and Functions

- `bld.SAMBA_SUBSYSTEM('oLschema2ldif-lib', source='lib.c', deps='samdb')`
- `bld.SAMBA_BINARY('oLschema2ldif', source='main.c', manpages='oLschema2ldif.1', deps='oLschema2ldif-lib cmdline')`
- `bld.SAMBA_BINARY('test_oLschema2ldif', source='test.c', deps='cmocka oLschema2ldif-lib', enabled=bld.CONFIG_SET('HAVE_FMEMOPEN'), install=False)`

## Control Flow

During build configuration, Waf declares the library first, then the installed utility, then the non-installed test binary conditional on `fmemopen()` support.

## State and Persistence Behavior

It affects build outputs and installed binaries/manpages. It has no runtime persistence.

## Dependencies and Integration Points

The converter library links against `samdb`; the CLI links against `cmdline`; the test links against cmocka. The test binary is local/non-installed.

## Risks and Edge Cases

Test coverage is absent on platforms without `fmemopen()`. Dependency drift in `lib.c` can require this fragment to add more explicit libraries.

## Test Signals

Successful build should produce `oLschema2ldif`, `oLschema2ldif.1`, and, where supported, `test_oLschema2ldif`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/utils/oLschema2ldif/wscript_build -->
