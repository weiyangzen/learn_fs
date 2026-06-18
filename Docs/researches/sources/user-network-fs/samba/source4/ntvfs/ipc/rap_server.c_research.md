# sources/user-network-fs/samba/source4/ntvfs/ipc/rap_server.c

## Purpose

`rap_server.c` provides the semantic server-side implementations behind the RAP dispatcher. It currently enumerates configured shares and returns an empty server enumeration result.

## Important APIs, Types, and Functions

Public functions are `rap_netshareenum()` and `rap_netserverenum2()`. `rap_netshareenum()` uses share APIs `share_get_context()`, `share_list_all()`, `share_get_config()`, `share_string_option()`, and `dcesrv_common_get_share_type()`. `rap_netserverenum2()` initializes success output with zero available servers.

## Control Flow

Share enumeration initializes output status and availability, obtains a share context, lists all share names, allocates a `union rap_share_info` array sized to the initial count, and iterates names. For each share whose config still exists, it copies the share name into the RAP fixed field, sets reserved byte, calculates share type, stores the comment string, frees the config, and increments the kept count. If a service disappears between list and config fetch, it logs a warning and skips it. Server enumeration just returns success with no entries.

## State and Persistence Behavior

This file reads share configuration but does not persist changes. Output arrays and strings are allocated under the caller-provided talloc context and consumed by `ipc_rap.c` for marshalling.

## Dependencies and Integration Points

It depends on Samba share configuration APIs, generated RAP types, generated SRVSVC/DCERPC types, RPC common share helpers, loadparm, and IPC prototypes. It is called only by RAP transaction handlers.

## Risks and Edge Cases

Inside the loop, most fields are written through `r->out.info[j]`, but `reserved1`, `share_type`, and `comment` are assigned via `r->out.info[i]`; if a prior share disappears and `j != i`, output can contain gaps or mismatched data. Share names are truncated with `strlcpy()` into fixed RAP fields. `rap_netserverenum2()` is a stub and may surprise clients expecting browse lists.

## Test Signals

Tests should cover normal share enumeration, disappearing shares during enumeration, long share names, comments and share types, no shares, and NetServerEnum2 empty-success behavior. A regression test should verify output indexing when one listed share cannot be configured.
