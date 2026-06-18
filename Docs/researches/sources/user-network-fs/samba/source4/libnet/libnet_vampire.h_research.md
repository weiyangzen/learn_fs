# sources/user-network-fs/samba/source4/libnet/libnet_vampire.h

## Purpose

`libnet_vampire.h` declares public request structures and an opaque callback-state type for Samba's vampire/replication workflows.

## Important APIs, Types, and Functions

`struct libnet_Vampire` describes a higher-level domain import request with input domain name, NetBIOS name, target directory, and output domain SID/name/error. `struct libnet_Replicate` describes lower-level replication input including domain, NetBIOS, targetdir, domain SID, realm, server, join password, and kvno. `struct libnet_vampire_cb_state` is forward-declared as private callback state.

## Control Flow

The header does not execute code. It lets callers pass structured inputs into vampire/replication implementations and carry opaque callback state without exposing internals.

## State and Persistence Behavior

The described operations persist local provisioned AD database and secrets/key material. The structures themselves are transient request containers.

## Dependencies and Integration Points

It depends on `struct dom_sid` and is included by BecomeDC/vampire C code, tests, and Python-facing replication support.

## Risks and Edge Cases

The request structures carry sensitive `join_password` and target directory paths; callers must manage lifetime and cleanup. Optional `targetdir` in `libnet_Replicate` needs clear implementation behavior.

## Test Signals

Compile-time integration plus BecomeDC/vampire tests validate this header. ABI drift affects both C callbacks and Python replication wrappers.
