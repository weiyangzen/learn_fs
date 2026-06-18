# sources/user-network-fs/samba/source4/ldap_server/wscript_build

## Purpose

This waf script declares Samba's AD DC LDAP server service module.

## Important APIs, Types, and Functions

It uses `bld.SAMBA_MODULE()` to define `service_ldap`, compiling `ldap_server.c`, `ldap_backend.c`, `ldap_bind.c`, and `ldap_extended.c`, generating `proto.h`, registering under the `service` subsystem, and using `server_service_ldap_init` as the init function.

## Control Flow

At build time it enables the module only when `bld.AD_DC_BUILD_IS_ENABLED()` is true.

## State and Persistence Behavior

There is no runtime state. It persists build graph metadata and generated prototypes.

## Dependencies and Integration Points

The dependency list connects LDAP server code to credentials, CLI LDAP, SAMDB, process model, GENSEC, host config, server GENSEC, and common auth.

## Risks and Edge Cases

Non-AD builds do not compile this module, so regressions may only surface in AD DC build lanes. Missing dependencies show up as link or generated-prototype failures.

## Test Signals

Signals include successful AD DC builds, generated `ldap_server/proto.h`, service registration, and selftests that start LDAP/LDAPS listeners.
