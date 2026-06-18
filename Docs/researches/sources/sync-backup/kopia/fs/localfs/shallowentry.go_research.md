## sources/sync-backup/kopia/fs/localfs/shallowentry.go

Purpose: defines shallow placeholder naming and a direct placeholder path adapter.

Important APIs/types/functions: `ShallowEntrySuffix`, `dirMode`, `TrimShallowSuffix`, `PlaceholderFilePath`, and `PlaceholderFilePath.DirEntryOrNil`.

Control flow, state, and persistence: suffix trimming normalizes visible entry names. `PlaceholderFilePath.DirEntryOrNil` reads metadata either from the path itself or from a nested `.kopia-entry` file when the path is a directory.

Dependencies and integration points: supports `shallow_fs.go` and any caller that needs to treat a placeholder path as `snapshot.HasDirEntryOrNil`.

Risks and test signals: risks include suffix collisions with real filenames and stale placeholder JSON. Direct tests are absent in this subset; behavior is integrated with shallow restore and localfs classification.
