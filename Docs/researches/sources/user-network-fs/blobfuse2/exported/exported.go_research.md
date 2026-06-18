## sources/user-network-fs/blobfuse2/exported/exported.go

Purpose: Public wrapper package exposing selected `internal` blobfuse2 types and helpers for custom component authors without importing internal packages directly.

Important APIs: Re-exports property flag constants, aliases `BaseComponent`, `Component`, `ComponentPriority`, `ObjAttr`, every component option struct in this subset, committed block types, and `handlemap.Handle`. `NewHandle` wraps `handlemap.NewHandle`. `ComponentPriorityWrapper` exposes priority constructors. `TruncateDirName` and `ExtendDirName` forward internal directory name helpers.

State and dependencies: Contains no state. Depends on `internal` and `internal/handlemap`; because aliases preserve identity, consumers interact with the same underlying types.

Integration points: This is the external extension boundary for pipeline components. It mirrors `internal` contracts used by loopback, xload, libfuse, and storage components.

Risks: Alias coverage must stay synchronized with `internal`; missing aliases can block plugin/custom component use. Exported constants use `uint16`-style iota while internal flags are currently `uint64`, so type assumptions can diverge. No direct tests in this subset.
