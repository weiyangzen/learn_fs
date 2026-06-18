# sources/user-network-fs/samba/source3/registry/reg_api.h

## Purpose

`reg_api.h` declares Samba’s high-level virtual registry API, mirroring common winreg operations for hive/key open, enumeration, query, mutation, security, version, and recursive delete.

## Important APIs, Types, and Functions

The header exports `reg_openhive`, `reg_openkey`, enumeration/query APIs, `reg_queryinfokey`, `reg_createkey`, `reg_deletekey`, `reg_setvalue`, `reg_deletevalue`, key security get/set, `reg_getversion`, `reg_deleteallvalues`, `reg_deletekey_recursive`, and `reg_deletesubkeys_recursive`.

## Control Flow

The API model is handle-based: callers open a hive or key with desired access and token, then pass the resulting `registry_key` to query, enumerate, mutate, or delete operations. Recursive helpers operate relative to a parent key.

## State and Persistence

The header defines no state, but its APIs operate on `struct registry_key`, `struct registry_value`, security descriptors, and backend-persistent registry data.

## Dependencies and Integration Points

It depends on Samba WERROR, TALLOC, security token/descriptor, NTTIME, and winreg create action types from surrounding includes. RPC winreg server code and registry utilities consume this public interface.

## Risks and Edge Cases

Callers must request sufficient desired access up front. The create/delete APIs return Windows-style WERROR values, so error mapping must be preserved by consumers.

## Test Signals

Compile-time tests should ensure signatures match implementation and generated RPC callers. API-level tests should use this header to exercise open/query/mutate/delete workflows.
