# sources/object-store/minio-mc/cmd/config-old.go

Purpose: Defines legacy MinIO Client configuration schemas from v1 through v9 so old JSON configs can still be represented during migration/compatibility paths. It does not perform I/O itself; it is a type catalog plus default constructors.

Important APIs/types/functions: `hostConfigV1` through `hostConfigV9`, `configV1` through `configV9`, and constructors `newConfigV*`. v7 and v8 add `loadDefaults` and `setHost`, while v9 introduces `SessionToken` and bucket `Lookup`.

Control flow: Each constructor allocates maps to avoid nil-map writes and sets the version string. v7/v8 default loaders insert known aliases only if missing, preserving user-provided entries.

State and persistence: In-memory structs mirror historic on-disk JSON layouts. Persistence is handled by newer config loaders elsewhere.

Dependencies/integration: Depends on `globalMCConfigVersion`, `defaultAccessKey`, and `defaultSecretKey` from the config package. Used by config migration code outside this subset.

Risks: Legacy field tags differ across versions, so migrations must preserve exact names. Defaults include public demo credentials and should not be treated as secure user secrets.

Test signals: No direct tests in this subset; behavior is indirectly covered by config loading/migration tests elsewhere.
