# sources/storage-engines/badger/badger/cmd/rotate.go

Purpose: implements `badger rotate`, which rewrites Badger key-registry metadata to rotate, remove, or enable encryption keys.

Important flow: flags provide old and new key paths. `doRotate` reads the old key with `getKey`, opens the key registry read-only for the DB directory with a rotation duration, reads the new key, updates options, and writes the key registry with `badger.WriteKeyRegistry`. `getKey` returns empty bytes for an empty path, enabling plaintext transitions, otherwise reads the entire file.

State and persistence: persistent mutation is the key registry in `sstDir`; DB data remains readable only with the new registry/key combination. Dependencies are Badger key-registry APIs, filesystem key reads, and root directory validation. Risks: key files are read whole without size validation, globals make tests order-sensitive, and plaintext/encrypted transitions depend on empty path semantics. Test signals in `rotate_test.go` cover wrong-key failure, encrypted-to-encrypted rotation, encrypted-to-plaintext, and plaintext-to-encrypted.
