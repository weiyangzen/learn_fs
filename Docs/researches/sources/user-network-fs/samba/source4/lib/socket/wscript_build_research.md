# sources/user-network-fs/samba/source4/lib/socket/wscript_build

## Purpose

This waf build script defines the source4 socket-related build units: interface discovery, IPv4 backend, Unix-domain backend, and the common `samba_socket` subsystem.

## Important APIs, Types, and Functions

It declares `netif` as a private library from `interface.c`, `socket_ip` and `socket_unix` as internal modules in subsystem `samba_socket`, and `samba_socket` as a subsystem built from `socket.c`, `access.c`, `connect_multi.c`, and `connect.c`.

## Control Flow

At configure/build time, waf evaluates these declarations to compile backend modules and link dependencies. Runtime backend selection still happens through `socket_getops_byname()`.

## State and Persistence Behavior

No runtime state is stored here. The script determines build graph persistence in generated waf metadata.

## Dependencies and Integration Points

`netif` depends on `samba-util`, `interfaces`, and `samba-hostconfig`. `socket_ip` depends on `samba-errors`; `socket_unix` depends on `talloc`; `samba_socket` has public deps `talloc` and `LIBTSOCKET` and private deps including `cli_composite`, `LIBCLI_RESOLVE`, `socket_ip`, `socket_unix`, and `access`.

## Risks and Edge Cases

Because `socket_ip` and `socket_unix` are internal modules but also direct dependencies of `samba_socket`, build graph changes can affect backend availability. IPv6 is conditional in C code, not expressed as a separate build target here.

## Test Signals

Successful waf configuration/compilation of `samba_socket`, plus local socket torture tests, are the main signals. Dependency changes should be validated by clean builds.
