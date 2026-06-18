## sources/sync-backup/syncthing/lib/protocol/indexid.go

Purpose: compact random identifier for device/folder index instances with binary marshal/unmarshal support.

Important APIs: `IndexID` type, `String`, `Marshal`, `Unmarshal`, and `NewIndexID`.

Control flow and state: marshal encodes the uint64 in big-endian bytes; unmarshal decodes exact-length data; `NewIndexID` reads random bytes and constructs an ID.

Dependencies and integration points: used in cluster config device metadata to identify remote index generations.

Risks: random generation must not silently return zero or reused IDs; unmarshal length validation is important for DB/wire compatibility.

Test signals: no direct tests in this subset.
