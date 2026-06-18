<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.c -->
# sources/user-network-fs/samba/source3/utils/py_net.c

## Purpose

`py_net.c` implements the `net_s3` Python extension module and exposes a `Net` object for Samba3-style domain join and leave operations.

## Important APIs, Types, and Functions

The Python type is `py_net_Type`, with C backing struct `py_net_Object` from `py_net.h`. Methods are `join_member()` and `leave()`. `check_ads_config()` validates member-server role, NetBIOS name length, and ADS realm configuration. `net_obj_new()` converts Python credentials and loadparm objects into Samba C pointers and stores an optional server address.

## Control Flow

Python constructs `net_s3.Net(creds, lp=None, server=None)`. `join_member()` allocates a `libnet_JoinCtx`, parses optional host/account/OS/password/debug/DNS flags, validates config unless the config backend is registry-backed, fills join flags and admin credentials, tries DNS-domain join first, retries NetBIOS-domain join on DC-not-found, optionally performs DNS updates, and returns `(domain_sid, dns_domain_name)`. `leave()` allocates `libnet_UnjoinCtx`, requires a realm, parses `keepAccount` and `debug`, requests account delete or disable semantics, calls `libnet_Unjoin()`, and returns a Python boolean.

## State and Persistence Behavior

Join and leave are persistent domain membership operations. They can create, delete, or disable machine accounts; modify local Samba configuration when registry-backed config is active; update secrets; and attempt DNS updates. The `Net` object owns a talloc frame, credentials pointer, loadparm context, server address pointer, and tevent context.

## Dependencies and Integration Points

It integrates Python C API, pytalloc/pyparam/pycredentials, Samba credentials, loadparm, `libnet_Join`, `libnet_Unjoin`, DNS update helper `net_ads_join_dns_updates()`, cmdline messaging, SID formatting, and dynamic config paths.

## Risks and Edge Cases

`net_obj_new()` stores `server_address` directly from Python argument parsing; object lifetime should be checked if Python frees or mutates the source object. Several allocation-error paths return without freeing the temporary context. Join treats DNS update failure as non-fatal after successful join, which callers must understand. `leave()` returns `False` after setting a Python exception on unjoin failure, an unusual combination for Python callers.

## Test Signals

Tests should cover constructor type validation, invalid ADS/member configuration, successful join return tuple, DC-not-found fallback to workgroup NetBIOS name, `noDnsUpdates`, registry versus file-backed config behavior, leave with and without `keepAccount`, and Python exception state on join/leave failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/py_net.c -->
