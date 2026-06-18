<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/wscript_build -->
# sources/user-network-fs/samba/source4/samba/wscript_build

## Purpose

This waf build fragment defines the source4 service framework, process-model framework, server utility subsystem, `samba` binary, and built-in process model modules.

## Important APIs, Types, and Functions

Targets include `service`, `process_model`, `samba_server_util`, the `samba` binary, `process_model_single`, `process_model_standard`, and `process_model_prefork`. It also configures autoproto headers `service_proto.h` and `process_model_proto.h`.

## Control Flow

During build, waf resolves these target declarations, links dependencies, and controls AD DC-only enablement with `AD_DC_BUILD_IS_ENABLED()`. Runtime module registration is affected by `init_function` and `internal_module` settings.

## State and Persistence Behavior

The file writes no runtime state. Persistent build products include libraries, modules, generated prototypes, and the installed `samba` binary under `${SBINDIR}`.

## Dependencies and Integration Points

The service library links tevent, messaging, socket, named-pipe auth, tsocket, credentials, and process model. The `samba` binary links command-line, GENSEC, registry, cluster, schannel, secrets, and server-util components. Process model modules link their model-specific dependencies.

## Risks and Edge Cases

Incorrect `internal_module` or dependency declarations change which process models are available at runtime. Missing `samba_server_util` in prefork or server deps would break log-tracing integration. AD DC gates must match code assumptions.

## Test Signals

Build tests should verify AD DC-enabled builds produce all three process model modules and the `samba` binary. Runtime smoke tests should start `samba --model=single`, `standard`, and `prefork`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/samba/wscript_build -->
