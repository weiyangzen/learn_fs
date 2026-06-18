# sources/user-network-fs/samba/source4/libnet/wscript_build

## Purpose

This Waf build script defines source4 libnet build targets, including the private `samba-net` library, a join/vampire helper library exposed for Python embedding, and Python extension modules for `samba.net` and `samba.dckeytab`.

## Important Targets

`bld.SAMBA_LIBRARY('samba-net', ...)` compiles many libnet sources including `userman.c` and `groupman.c`, generates `libnet_proto.h`, and depends directly on `INIT_SAMR`. Its public dependencies include credentials, DCE/RPC, SAMR, LSA/SRVSVC/DRSUAPI NDR bindings, resolve/find-dc helpers, NETLOGON ping, schannel, auth, NDR, SMB password parsing, SAM sync, tsocket, and GnuTLS helpers.

`bld.SAMBA_LIBRARY(name, ...)` builds the private, Python-embedded `samba-net-join` library from join and vampire sources when Python builds are enabled. `python_net` builds `samba/net.so` from `py_net.c`, and `python_dckeytab` builds `samba/dckeytab.so` when AD DC support is enabled.

## Control Flow And State

The script is declarative Waf metadata. It derives embedded Python library names with `bld.pyembed_libname()` and uses configuration predicates such as `bld.PYTHON_BUILD_IS_ENABLED()` and `bld.CONFIG_SET('AD_DC_BUILD_IS_ENABLED')` to gate optional artifacts.

## Dependencies And Integration Points

The script is the integration point that pulls `userman.c` into `samba-net`. It also links Python modules to `pyrpc_util`, `pytalloc-util`, `pyldb-util`, provisioning, Kerberos, and database glue as needed.

## Risks

Dependency lists are dense; missing or duplicated dependency names can create build-order or link failures that only appear in selected feature configurations. Because `samba-net` is private, ABI exposure is lower, but Python modules depend on the private libraries being built with Python embedding support.

## Test Signals

Signals include successful Waf configure/build under Python-enabled and Python-disabled configurations, AD DC enabled and disabled builds, and import tests for `samba.net` and `samba.dckeytab` when enabled.
