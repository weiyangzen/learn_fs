# sources/sync-backup/kopia/internal/indextest/indextest.go

Purpose: provides detailed diffing for `repo/content/index.Info` values in tests.

Important APIs/types/functions: `InfoDiff`, `index.Info`, `Timestamp`, `reflect.TypeFor`, and optional string-prefix ignore filters.

Control flow: `InfoDiff` compares each relevant exported field and derived timestamp, appending human-readable differences. It then checks the method count on `index.Info` to force maintainers to revisit this helper when the type's behavior changes. Finally it filters differences whose messages start with any ignored prefix.

State/persistence behavior: no state is persisted. It inspects in-memory index metadata that corresponds to repository content index records.

Dependencies/integration: used by content index tests to produce clearer mismatch output than a raw struct comparison. It integrates with `repo/content/index` type evolution.

Risks/test signals: field coverage is manual. The reflection method-count guard catches some API drift but not newly added fields, so maintainers still need to update comparisons when `index.Info` changes.
