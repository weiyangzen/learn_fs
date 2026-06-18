# sources/user-network-fs/samba/source3/registry/reg_api_util.h

## Purpose

`reg_api_util.h` declares utility APIs layered over `reg_api.c`.

## Important APIs, Types, and Functions

- `reg_open_path()` opens a complete registry path containing a hive prefix and optional subkey suffix.

## Control Flow

The declared API collapses the usual `reg_openhive()` plus `reg_openkey()` sequence into one call.

## State and Persistence

The header owns no state. Returned `registry_key` objects are allocated under the caller-provided TALLOC context.

## Dependencies and Integration Points

It depends on registry key and security token types from surrounding registry headers. It is intended for utility callers that parse user-provided registry paths.

## Risks and Edge Cases

Callers still need to pass the desired access and security token appropriate for the final key; the utility does not bypass registry access checks.

## Test Signals

Compile-time coverage plus functional tests through `reg_open_path()` are sufficient.
