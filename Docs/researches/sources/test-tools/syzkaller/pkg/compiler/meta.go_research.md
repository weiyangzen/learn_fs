# sources/test-tools/syzkaller/pkg/compiler/meta.go

Purpose: Handles syzlang file-level metadata such as automatic descriptions, no-extract markers, and supported architectures.

Important APIs/types/functions: `Meta`, `Meta.SupportsArch`, `FileList`, `compiler.fileMeta`, `compiler.fileList`, `metaTypes`, `metaAutomatic`, `metaNoExtract`, `metaArches`, and `metaArch`.

Control flow: `FileList` selects any target for an OS and delegates to a compiler to parse metadata. `fileList` scans AST nodes by basename, validates meta node types through `checkTypeImpl`, and sets `Automatic`, `NoExtract`, or `Arches`. `fileMeta` lazily builds and caches the map. `filterArch` in `compiler.go` consumes `SupportsArch`.

State and persistence behavior: Metadata is stored in the compiler's in-memory `fileMetas` map. No disk persistence.

Dependencies/integration points: Depends on `ast` and `targets`. Used by compiler filtering, syscall generation (`Automatic` attr), const collection, and unused-const collection.

Risks: Metadata is keyed by `filepath.Base(pos.File)`, so files with the same basename in different dirs could collide if descriptions include paths that are not unique by base. `FileList` returns nil for unknown OS.

Test signals: Covered indirectly by compiler testdata and full sys description compilation across arches.
