# sources/user-network-fs/samba/source4/libnet/libnet_share.h

## Purpose

`libnet_share.h` declares request/response structures for libnet share operations over SRVSVC.

## Important APIs, Types, and Functions

`enum libnet_ListShares_level`, `enum libnet_AddShare_level`, and `enum libnet_DelShare_level` distinguish generic and SRVSVC backends. `struct libnet_ListShares` carries `server_name`, requested info `level`, optional resume pointers, and a returned `union srvsvc_NetShareCtr`. `struct libnet_AddShare` carries server name and a level-2 share definition. `struct libnet_DelShare` carries server and share names.

## Control Flow

The header has no code. Implementation dispatch is simple and currently SRVSVC-only in `libnet_share.c`.

## State and Persistence Behavior

The structures describe remote server share state. Add/delete mutate persistent remote configuration; list returns in-memory counters. Pointer ownership is delegated to implementation memory contexts.

## Dependencies and Integration Points

It includes generated `srvsvc.h` for share types. Callers include Samba management utilities and torture tests.

## Risks and Edge Cases

The header exposes resume-handle fields, but the current implementation does not fully honor them. Callers should not assume paging works unless implementation support is added.

## Test Signals

Compile-time consumers and SRVSVC torture tests validate the contract. Tests should compare header-exposed resume behavior to implementation behavior.
