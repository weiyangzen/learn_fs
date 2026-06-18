## sources/sync-backup/kopia/internal/bigmap/bigmap_map.go

Purpose: exported encrypted value map built on `internalMap`.

Important APIs/types/functions: `Map`, `NewMap`, `NewMapWithOptions`, `PutIfAbsent`, `Get`, `Contains`, `Close`, and `decrypt`.

Control flow, state, and persistence: constructor creates a random AES-256 key and GCM AEAD. Non-empty values are encrypted with nonce bytes that contain an atomically incremented 64-bit counter and use the map key as associated data. The encrypted blob including nonce is stored in `internalMap`; empty values store nil. State is process-local and not durable.

Dependencies and integration points: used where a memory-efficient content/object ID map with confidential values is needed. Depends on `gather.WriteBuffer`, AES-GCM, and `internalMap`.

Risks and test signals: nonce is 12 bytes but only 8 are explicitly populated, leaving four zero bytes; uniqueness still follows the counter. Counter wrap panics. Decryption failure surfaces as an error. Tests cover growing encrypted maps and retrieval.
