# sources/storage-engines/badger/key_registry.go

## Purpose
`key_registry.go` manages Badger data-encryption keys. It persists generated data keys in `KEYREGISTRY`, validates the user storage key through encrypted sanity text, supports key rotation, and rewrites registry files atomically.

## Important APIs, Types, and Functions
- Constants: `KeyRegistryFileName`, `KeyRegistryRewriteFileName`.
- `sanityText`: plaintext used to validate the storage key.
- `KeyRegistry`: synchronized map of `pb.DataKey` by id, `lastCreated`, `nextKeyID`, file pointer, and options.
- `KeyRegistryOptions`: registry directory, read-only flag, storage encryption key, rotation duration, and in-memory mode.
- Lifecycle: `newKeyRegistry`, `OpenKeyRegistry`, `Close`.
- Iteration/read: `keyRegistryIterator`, `newKeyRegistryIterator`, `validRegistry`, `(*keyRegistryIterator).next`, `readKeyRegistry`.
- Persistence: `WriteKeyRegistry`, `storeDataKey`.
- Access/rotation: `DataKey`, `LatestDataKey`.

## Control Flow and State
`OpenKeyRegistry` validates encryption-key length, short-circuits in-memory mode, opens or creates `KEYREGISTRY`, reads existing keys, and keeps the file open for append in read-write mode. `validRegistry` reads IV and sanity text and decrypts it when a storage key exists. `LatestDataKey` returns the current key if it is within the rotation duration, otherwise it generates random key bytes and IV, appends an encrypted protobuf record, updates in-memory state, and returns the plaintext key.

## Persistence Behavior
The registry file layout is IV + sanity text + repeated records of 4-byte length, 4-byte Castagnoli CRC, and marshaled `pb.DataKey`. Data-key bytes are XOR-encrypted with the storage key and per-key IV before writing, then restored in memory. `WriteKeyRegistry` writes a complete temp file (`REWRITE-KEYREGISTRY`), closes it, renames it over `KEYREGISTRY`, and calls `syncDir`.

## Dependencies and Integration Points
Used by Badger encryption paths and value-log/table encryption through data key lookup. Depends on `pb.DataKey`, protobuf marshal/unmarshal, AES block size, random bytes, CRC, Badger `y` crypto/file helpers, and platform `syncDir`.

## Risks and Edge Cases
`storeDataKey` mutates `k.Data` in place while encrypting/decrypting, so error paths must restore plaintext carefully. Map iteration in `WriteKeyRegistry` is nondeterministic, though `readKeyRegistry` reconstructs by key id. Read-only open of a missing registry returns an empty registry. File append in `LatestDataKey` writes but does not explicitly call file sync here.

## Test Signals
`key_registry_test.go` covers build/reopen, rewrite after deletion, storage-key mismatch, encryption/decryption round-trip, and in-memory behavior.
