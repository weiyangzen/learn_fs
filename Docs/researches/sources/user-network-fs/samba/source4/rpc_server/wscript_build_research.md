<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/wscript_build -->
# sources/user-network-fs/samba/source4/rpc_server/wscript_build

## Purpose

This waf build fragment declares Samba source4 DCE/RPC server libraries, subsystems, endpoint modules, service integration, and a DNS utility selftest binary.

## Important APIs, Types, and Functions

The script uses waf helper declarations such as `bld.SAMBA_SUBSYSTEM`, `bld.SAMBA_LIBRARY`, `bld.SAMBA_MODULE`, and `bld.SAMBA_BINARY`. It defines `DCERPC_SHARE`, `DCERPC_COMMON`, the public `dcerpc_server` library, endpoint modules including `dcerpc_epmapper`, `dcerpc_remote`, `dcerpc_srvsvc`, `dcesrv_samr`, `dcerpc_winreg`, `dcerpc_netlogon`, `dcerpc_lsarpc`, `dcerpc_backupkey`, `dcerpc_drsuapi`, `dcerpc_browser`, `dcerpc_eventlog`, `dcerpc_dnsserver`, and the `service_dcerpc` service module.

## Control Flow

At configure/build time, waf evaluates the declarations and emits targets subject to feature gates such as `AD_DC_BUILD_IS_ENABLED()`, `WITH_NTVFS_FILESERVER`, and `ENABLE_SELFTEST`. Module entries bind C sources to subsystem names and init functions so Samba module loading can register endpoint servers.

## State and Persistence Behavior

No runtime state is stored here. The persistent outputs are build artifacts, generated prototype headers such as `dcerpc_server_proto.h` and `samr/proto.h`, pkg-config metadata, installed binaries/libraries, and module objects.

## Dependencies and Integration Points

The file is a central integration point between endpoint C implementations, generated NDR libraries, Samba authentication/security/DSDB libraries, and the source4 service framework. `dcerpc_winreg` specifically links `winreg/rpc_winreg.c` with `registry` and `ndr-standard`.

## Risks and Edge Cases

Incorrect `enabled` gates can silently remove endpoints from an AD DC build. Dependency omissions tend to surface late as link errors or module-load failures. Internal versus external module choices affect static module registration and runtime module availability.

## Test Signals

Build tests should validate AD DC and non-AD configurations, `WITH_NTVFS_FILESERVER` toggles, selftest-enabled `dcerpc_rpcecho`, and endpoint startup through the `service_dcerpc` module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/rpc_server/wscript_build -->
