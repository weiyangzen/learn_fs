# sources/test-tools/syzkaller/pkg/codesearch/database.go

Purpose: Defines the JSON schema and merge/finalization behavior for codesearch entity databases emitted by clangtool.

Important APIs/types/functions: `Database`, `Definition`, `FieldInfo`, `Reference`, `LineRange`, `EntityKind`, `RefKind`, custom `String`/`MarshalJSON`/`UnmarshalJSON` methods, `DatabaseFormatHash`, `Database.Merge`, `Database.Finalize`, `Database.SetSourceFile`, and `intern`.

Control flow: Each clangtool output is merged by unique key `<kind>-<name>-<body file>`. New definitions are verified for body/comment line ranges, string fields are interned, and duplicate keys are ignored. `Finalize` collects merge-cache values into `Definitions`, sorts by the remembered stable key, and clears merge caches. `SetSourceFile` normalizes paths and marks static definitions as non-static if their body is in a different `.c` file than the compile unit.

State and persistence behavior: The public persisted state is JSON `definitions`. `mergeCache`, `reverseCache`, and `stringCache` are transient merge-time structures. `DatabaseFormatHash` hashes the generated JSON schema plus a semantic version string for cache invalidation by callers.

Dependencies/integration points: Implements the `clangtool.OutputDataPtr` contract. Uses `jsonschema.For[Database]` and `pkg/hash` to derive the format hash, and `clangtool.Verifier` to reject invalid source ranges during merge.

Risks: `EntityKind.String` and `RefKind.String` index directly into name arrays; invalid enum values could panic if constructed outside JSON parsing expectations. Duplicate definition identity ignores type/signature and line span, so conflicting definitions with same kind/name/file collapse silently. The comment above `SetSourceFile` has a typo but not behavioral impact.

Test signals: Validated indirectly by clangtool golden JSON, command tests, path verifier checks, and merge/finalize behavior in `tooltest.LoadOutput`.
