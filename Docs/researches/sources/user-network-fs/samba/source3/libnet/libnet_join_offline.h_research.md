# sources/user-network-fs/samba/source3/libnet/libnet_join_offline.h

## Purpose

Declares helper APIs for Offline Domain Join provision data composition and extraction.

## Important APIs, Types, and Functions

Declares `libnet_odj_compose_ODJ_PROVISION_DATA`, `libnet_odj_find_win7blob`, and `libnet_odj_find_joinprov3`, operating on generated `ODJ_PROVISION_DATA`, `ODJ_WIN7BLOB`, `OP_JOINPROV3_PART`, and `libnet_JoinCtx` types.

## Control Flow

Provisioning code composes ODJ data from a populated join context. Offline-join code extracts domain/machine data and provider3 RID/SID information from incoming provision data.

## State and Persistence Behavior

No header state. Implementations allocate outputs under caller talloc contexts and expose data that may include machine passwords.

## Dependencies and Integration Points

Consumed by `libnet_join.c` and any provisioning callers that include generated ODJ declarations.

## Risks and Test Signals

Risks are contract-level: invalid generated structures or mishandled sensitive data. Tests should compile include users and verify compose/find behavior through the implementation.
