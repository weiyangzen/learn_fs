# sources/storage-engines/pebble/comparer.go

Purpose: Re-exports comparer-related internal base types through the public `pebble` package.

Important APIs/types/functions: Type aliases expose `Compare`, `Equal`, `AbbreviatedKey`, `Separator`, `Successor`, `Split`, and `Comparer`. Variables expose `DefaultComparer` and `CheckComparer`.

Control flow: No runtime control flow beyond package variable initialization. Type aliases retain identity with `internal/base` types.

State and persistence: No persisted state. Exported comparer values are shared configuration used by options, table metadata construction, manifest ordering, and tests.

Dependencies and integration: Depends only on `github.com/cockroachdb/pebble/internal/base`. This file is a public API boundary for key comparison behavior.

Risks: Changes are public API changes. Because aliases expose base type identity, internal comparer shape changes propagate externally. Tests in this subset rely heavily on `DefaultComparer.Compare`.

Test signals: No direct tests, but indirect coverage is broad through compaction, picker, manifest, and datadriven tests using `DefaultComparer` and `Options.Comparer`.
