# File Research: sources/os/linux/linux-stable/fs/afs/protocol_yfs.h

## Scope

Declares YFS/RxYFS service IDs, operation numbers, XDR wire structures, helpers, volume flags, lock types, and capability bits.

## APIs And Behavior

- Defines `YFS_FS_SERVICE`, `YFS_CM_SERVICE`, callback and fileserver operation opcodes, including 64-bit fetch/store, ACL, rename, and symlink operations.
- Provides packed XDR structures for YFS FIDs, status, callbacks, store status, volume sync/status, and RPC flags.
- Provides `xdr_to_u64()` and `u64_to_xdr()` conversion helpers for split 64-bit XDR values.
- Defines YFS volume status flags and lock type constants.

## Dependencies And Risks

YFS client marshalling/unmarshalling depends on exact packing and byte-order conversion. Signed lock constants and packed 64-bit fields are protocol ABI details.
