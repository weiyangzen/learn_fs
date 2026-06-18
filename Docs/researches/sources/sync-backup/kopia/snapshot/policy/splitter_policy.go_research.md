# sources/sync-backup/kopia/snapshot/policy/splitter_policy.go

Purpose: defines the content splitter algorithm policy used while uploading files.

Important APIs/types/functions: `SplitterPolicy`, `SplitterPolicyDefinition`, `SplitterForFile`, and `Merge`. The only policy field is `Algorithm`, with provenance stored in `SplitterPolicyDefinition.Algorithm`.

Control flow: `SplitterForFile` currently ignores the `fs.Entry` and returns the configured algorithm directly. `Merge` uses the shared `mergeString` helper to fill an unset child value from a source policy and record the defining `snapshot.SourceInfo`.

State and persistence: no persistence in this file; values become persistent only as part of broader policy serialization.

Dependencies and integration points: used by upload/chunker selection through policy evaluation and the `fs.Entry` interface, leaving room for future per-file algorithm decisions.

Risks and test signals: the entry parameter is unused, so any intended file-sensitive splitter selection would require new logic. Reflection-based policy merge tests cover field presence and merge behavior.
