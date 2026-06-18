# sources/user-network-fs/samba/source4/libnet/userinfo.h

## Purpose

`userinfo.h` declares the lower-level SAMR userinfo request/response structure and monitor payloads used by `userinfo.c`.

## Important APIs, Types, and Functions

`struct libnet_rpc_userinfo` contains input `policy_handle domain_handle`, optional `username`, optional string `sid`, and query `level`; output is `union samr_UserInfo info`.

Monitor structures are `msg_rpc_open_user` with RID/access mask, `msg_rpc_query_user` with query level, and `msg_rpc_close_user` with RID.

## Control Flow

The presence of `sid` selects the direct open-user path; otherwise implementation uses `username` lookup first. Monitor structs are sent at open, query, and close stages.

## State and Persistence Behavior

The structure is transient and read-only with respect to directory data. The remote operation opens/closes a user handle and returns copied SAMR info.

## Dependencies and Integration Points

It includes generated SAMR types and is consumed by `userinfo.c`, `libnet_user.c`, and torture tests. It also shares monitor-message conventions with other libnet RPC helpers.

## Risks and Edge Cases

The contract does not state whether `sid` and `username` are mutually exclusive or what happens if neither is set. The SID is a string rather than a typed `dom_sid`, so callers rely on implementation parsing.

## Test Signals

Direct sync/async userinfo torture tests validate both lookup modes and returned `samr_UserInfo` content.
