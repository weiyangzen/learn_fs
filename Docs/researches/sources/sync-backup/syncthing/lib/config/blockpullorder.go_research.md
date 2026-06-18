# sources/sync-backup/syncthing/lib/config/blockpullorder.go

Purpose: Text-marshaled enum for file block pull order.

Important APIs/types/functions: `BlockPullOrder` has `BlockPullOrderStandard`, `BlockPullOrderRandom`, and `BlockPullOrderInOrder`. `String`, `MarshalText`, and `UnmarshalText` convert to/from `standard`, `random`, and `inOrder`.

Control flow: Unknown text values default to standard and return nil.

State and persistence behavior: Used in folder config serialization. The fixture config uses `random`, showing persisted XML integration.

Dependencies and integration points: Consumed by folder pulling/config code outside this subset and by config REST handlers that marshal/unmarshal folder options.

Risks: Silent fallback to standard can mask invalid config. String values are user-visible config compatibility contracts.

Test signals: No direct test in this subset; config API tests indirectly round-trip folder configuration.
