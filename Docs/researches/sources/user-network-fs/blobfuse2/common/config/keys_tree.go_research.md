# sources/user-network-fs/blobfuse2/common/config/keys_tree.go
## sources/user-network-fs/blobfuse2/common/config/keys_tree.go

Purpose: implements a dot-key tree used by the config layer to map env vars and flags onto nested config structs after Viper unmarshalling.

Important APIs/types/functions: `STRUCT_TAG`, `TreeNode`, `Tree`, `NewTree`, `NewTreeNode`, `Insert`, `Print`, `GetSubTree`, `parseValue`, `MergeWithKey`, `Merge`, `isPrimitiveType`, `assignToField`, and `getIdxFromField`.

Control flow: `Insert` splits keys on `.` and creates child nodes down to the leaf value. `Merge` starts at root and recursively overlays matching tree values onto struct fields; `MergeWithKey` does the same for a subtree. Field names come from the `config` tag or lowercased field name. For struct fields it recurses; for pointer fields it recurses into `Elem`; for primitives it calls `getValue`, parses string values into the target kind when needed, and sets the field.

State and persistence: all state is in-memory tree nodes storing arbitrary values, typically env var names or pflag pointers. No persistence.

Dependencies/integration: reflection, strconv parsing, and config parser merge callbacks.

Risks: pointer handling assumes non-nil pointers and can panic on nil pointer fields. `assignToField` silently ignores unparseable string values. `parseValue` uses bit sizes matching target kinds, but `int`/`uint` use bit size 0, which is platform-dependent. `Print` writes directly to stdout and is diagnostic only.

Test signals: `keys_tree_test.go` covers primitive parsing success/failure and primitive kind classification. Integration with `Merge` is covered indirectly by `config_test.go`.
