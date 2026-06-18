# sources/object-store/minio/cmd/config-common.go

## Purpose
`config-common.go` provides low-level object-store helpers for reading, writing, deleting, and checking MinIO configuration objects in `.minio.sys`.

## Important APIs, Types, And Functions
`errConfigNotFound` normalizes missing or empty config objects. `readConfigWithMetadata` reads an object through `objectIO.GetObjectNInfo`, returns bytes plus `ObjectInfo`, and maps object-not-found/empty content to `errConfigNotFound`. `readConfig` drops metadata. `objectDeleter` narrows delete dependencies. `deleteConfig` deletes exact config objects via prefix-delete optimization. `saveConfigWithOpts` wraps bytes in a SHA256 `hash.Reader` and writes through `PutObject`. `saveConfig` uses `MaxParity`. `checkConfig` probes object existence through `GetObjectInfo`.

## Control Flow
Read paths open a `GetObjectReader`, drain it fully, close it, and classify errors. Write paths construct a hash-validated reader and hand off to object-layer persistence. Delete/check paths translate object-not-found into the shared config sentinel.

## State And Persistence Behavior
All state lives as objects under `minioMetaBucket`. Writes use object-layer options, defaulting to maximum parity for durability. Deletes use `DeletePrefixObject` for exact-object optimization.

## Dependencies And Integration Points
These helpers are used by server config, config history, scanner state, background heal info, and data usage persistence. They integrate with MinIO object APIs, HTTP range reader conventions, `internal/hash`, `getSHA256Hash`, and `NewPutObjReader`.

## Risks And Test Signals
The helpers treat empty config files as missing, which is intentional but can hide corruption as reinitialization higher up. Full-object reads can be expensive for large configs, though config objects are expected small. There are no direct tests in this subset; behavior is exercised indirectly by config and scanner tests.
