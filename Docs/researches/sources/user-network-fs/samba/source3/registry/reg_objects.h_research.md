# sources/user-network-fs/samba/source3/registry/reg_objects.h

## Purpose
`reg_objects.h` declares opaque registry value and subkey container APIs for source3 registry code.

## Important APIs, Types, And Functions
It forward-declares `struct regval_blob`, `struct regval_ctr`, and `struct regsubkey_ctr`, then exposes subkey container creation, reset, sequence numbers, add/delete/existence/count/indexed lookup, and value container creation, accessors, lookup, composition, add/copy/delete, string helpers, and sequence numbers.

## Control Flow
Users allocate containers with the init functions, pass them to backend fetch/store operations, inspect counts and entries, and free them through the talloc parent. The implementation requires the objects themselves to be talloc-allocated because internal data is attached to their talloc context.

## State And Persistence
The header describes transient in-memory containers. Sequence numbers expose backend freshness state but do not persist by themselves.

## Dependencies And Integration Points
Backends in this subset use the API to synthesize values and enumerate subkeys. Registry database and RPC-facing code use it as the common exchange format.

## Risks And Test Signals
Because structures are opaque, ABI users must not stack-allocate or embed them. Compile and runtime tests should cover correct init/free patterns, sequence-number handling, and all lookup paths. Tests should also validate string value helpers use Windows registry encodings as expected.
