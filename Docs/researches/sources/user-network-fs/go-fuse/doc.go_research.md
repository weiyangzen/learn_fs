# sources/user-network-fs/go-fuse/doc.go

Purpose: repository-level package documentation for the module root package `lib`.

Important content: describes go-fuse as Go bindings for writing FUSE filesystems and points users toward the modern `fs` package documentation plus older deprecated `pathfs` and `nodefs` APIs.

Control flow/state: none; documentation-only source file.

Dependencies/integration: package declaration allows root package documentation in Go tooling. Risks are documentation drift because links still point at godoc URLs and mention older APIs. Test signal is build/doc generation success; no behavioral tests are needed for this file.
