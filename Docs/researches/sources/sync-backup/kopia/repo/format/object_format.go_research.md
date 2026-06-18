# sources/sync-backup/kopia/repo/format/object_format.go

## Purpose
Defines object-level repository formatting options.

## Important APIs, Types, And Functions
`ObjectFormat` contains the `Splitter` string, which names the splitter used to break objects into content chunks.

## Control Flow
No functions or runtime control flow.

## State And Persistence
`ObjectFormat` is embedded in `RepositoryConfig` and persisted encrypted inside `kopia.repository`.

## Dependencies And Integration Points
Used by object writer/reader configuration through `format.Manager.ObjectFormat` and repository initialization options.

## Risks And Edge Cases
Invalid splitter names are not validated in this file; validation is expected where splitters are resolved.

## Test Signals
Upgrade-lock tests initialize repositories with `ObjectFormat{Splitter: "FIXED-1M"}` and then write objects, indirectly exercising persistence and retrieval.
