# sources/sync-backup/syncthing/lib/config/copyrangemethod.go

## sources/sync-backup/syncthing/lib/config/copyrangemethod.go

Purpose: Defines user-facing configuration values for file clone/copy-range strategy and maps them to filesystem-layer strategies.

Important APIs/types/functions: `CopyRangeMethod` enum supports `standard`, `ioctl`, `copy_file_range`, `sendfile`, `duplicate_extents`, and `all`. Methods are `String`, `ToFS`, `MarshalText`, `UnmarshalText`, and `ParseDefault`.

Control flow and state: Stateless enum conversion. Unknown strings default to `CopyRangeMethodStandard`, and unknown enum values stringify as `unknown` while `ToFS` falls back to filesystem standard behavior.

Dependencies and integration: Used by `FolderConfiguration.CopyRangeMethod` and passed down to `lib/fs` copy/clone operations. `structutil` can call `ParseDefault` for default tags.

Risks and test signals: Silent fallback prevents config-load failures but may mask invalid settings. No direct test in this subset, but it is exercised indirectly through folder default loading and XML/JSON serialization.
