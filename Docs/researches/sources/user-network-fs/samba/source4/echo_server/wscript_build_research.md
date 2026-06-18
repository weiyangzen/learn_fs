# sources/user-network-fs/samba/source4/echo_server/wscript_build

## Purpose

`source4/echo_server/wscript_build` registers the echo server example as a Samba service module named `ECHO`.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_MODULE()` with source `echo_server.c`, subsystem `service`, init function `server_service_echo_init`, dependencies `samba-hostconfig LIBTSOCKET LIBSAMBA_TSOCKET`, `local_include=False`, and `enabled=bld.CONFIG_GET('ENABLE_SELFTEST')`.

## Control Flow

During Waf build generation, the module is declared only when `ENABLE_SELFTEST` is configured. If enabled, Samba's service subsystem can load/register the module through `server_service_echo_init()`.

## State and Persistence Behavior

The build file has no runtime state. It controls whether the echo service artifact exists in selftest builds and keeps the sample service out of normal builds.

## Dependencies and Integration Points

The module declaration links the echo service to host configuration and tsocket libraries. Its `subsystem='service'` value is the integration point with Samba's task/service registration mechanism.

## Risks and Edge Cases

Tests or examples that expect the echo service must ensure `ENABLE_SELFTEST` is set. Missing tsocket dependencies would break linkage, while changing `init_function` without matching the C symbol would prevent registration.

## Test Signals

The main signal is a selftest-enabled build producing the `ECHO` service module and successfully resolving `server_service_echo_init`.
