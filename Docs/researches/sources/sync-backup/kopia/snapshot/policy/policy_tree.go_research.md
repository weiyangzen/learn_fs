# sources/sync-backup/kopia/snapshot/policy/policy_tree.go

Purpose: builds and queries an inherited policy tree keyed by relative source paths. It provides the default policy values used when no explicit policy exists and exposes tree nodes that distinguish explicitly defined policy from inherited policy.

Important APIs/types/functions: global `DefaultPolicy`, `DefaultDefinition`, `Tree`, `DefinedPolicy`, `EffectivePolicy`, `IsInherited`, `Child`, `BuildTree`, `buildTreeNode`, and `childrenWithPrefix`. Defaults include files, compression, metadata compression, error handling, logging, retention, scheduling, OS snapshot, and upload policy defaults.

Control flow: `BuildTree` starts at `"."`, chooses the defined policy for that path or the passed default, then recursively groups descendants by the next path element. `Child` walks slash-separated names, treats `""` and `"."` as the current node, returns explicit children when present, and synthesizes inherited nodes otherwise.

State and persistence: state is an in-memory immutable-ish tree after construction; nil trees are valid and map to `DefaultPolicy`.

Dependencies and integration points: used by upload, estimate, scheduling, and policy lookup code to carry source-specific policy down filesystem traversal.

Risks and test signals: path normalization is caller-sensitive; paths are expected to be relative and dot-rooted. Tests assert inherited flags and effective policies across missing, nested, and dot path segments.
