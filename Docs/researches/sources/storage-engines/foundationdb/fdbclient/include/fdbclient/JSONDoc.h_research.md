# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/JSONDoc.h

## Purpose
Provides a convenience wrapper around `json_spirit::mObject` for path-based JSON reads, writable path creation, value insertion, subdocument access, and merge-operator application. It is used where FoundationDB needs lightweight structured status, configuration, credential, or metadata manipulation.

## Important APIs, Types, And Functions
Constructors attach to const or writable `mObject`/`mValue` instances. `has(path, split)` walks dot-separated object paths and updates `last()` on success. `create()`, `put()`, and `subDoc()` force writable object paths into existence. `mergeOperator`, `mergeOperatorWrapper`, `getOperator`, `mergeInto`, `mergeValueInto`, and `cleanOps` implement object merging with operators such as `$max`, `$min`, and `$sum`. `absorb()` merges another document. `get()`, `tryGet()`, `at()`, `operator[]`, `obj()`, and `wobj()` expose read/write access. `expires_reference_version` supports `$expires` merge semantics.

## Control Flow
Read paths iterate segment by segment, requiring intermediate values to be objects and returning false for missing keys. Writable creation similarly walks the path but replaces non-object intermediates with objects and creates missing entries. Merge routines are declared here and implemented elsewhere, recursively combining source into destination while honoring operator objects and later removing unmatched operators.

## State And Persistence Behavior
`JSONDoc` does not own JSON storage. It holds pointers to a readable object and, when permitted, a writable object. It also caches the last successfully found value pointer. Changes mutate the attached object in memory; persistence only occurs when callers serialize or store that object externally.

## Dependencies And Integration Points
The header depends on `json_spirit` reader/writer templates and Flow error/assertion support. It is integrated by blob credential handling, JSON status construction, schema validation, and metadata merging paths.

## Risks And Test Signals
Risks include stale `last()` use after mutation, exceptions when intermediate path values are not objects, accidental overwrites from `create()`, dot-containing keys when `split` is wrong, and mismatched merge-operator types. Test signals should include const vs writable construction, split and non-split paths, type mismatch exceptions, recursive merge behavior, operator cleanup, and expiration behavior with `expires_reference_version`.
