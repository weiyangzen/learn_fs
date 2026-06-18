<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.h -->
# sources/user-network-fs/ksmbd-tools/adduser/md4_hash.h

## Purpose

Declares the MD4 context and API used by user password hashing.

## Important APIs, Types, and Functions

Defines `MD4_BLOCK_WORDS`, `MD4_HASH_WORDS`, `struct md4_ctx`, and functions `md4_init`, `md4_update`, and `md4_final`.

## Control Flow

Callers initialize the context, feed arbitrary byte chunks, and finalize into a 16-byte digest.

## State and Persistence Behavior

The context is caller-owned transient memory and is zeroed by finalization.

## Dependencies and Integration Points

Used by user_admin.c and implemented by md4_hash.c.

## Risks and Edge Cases

Callers must provide a sufficiently large output buffer and must not reuse a finalized context without reinitialization.

## Test Signals

Compile tests and known digest vectors cover the declaration contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.h -->
