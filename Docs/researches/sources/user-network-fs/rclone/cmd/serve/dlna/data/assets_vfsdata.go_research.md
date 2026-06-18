# sources/user-network-fs/rclone/cmd/serve/dlna/data/assets_vfsdata.go

## Purpose

This generated file embeds DLNA service XML, the root descriptor template, and rclone icon PNGs as an `http.FileSystem`.

## Important APIs, Types, and Functions

`Assets` is a generated `http.FileSystem`. Generated types include `vfsgen...FS`, `CompressedFileInfo`, `CompressedFile`, `FileInfo`, `File`, `DirInfo`, and `Dir`. Methods implement `Open`, `Read`, `Seek`, `Close`, `Stat`, `Readdir`, and metadata accessors.

## Control Flow

`Open` cleans the path, finds an embedded entry, and returns a gzip-backed reader for compressed XML/template assets, a bytes reader for PNGs, or a directory wrapper. Compressed reads reset and fast-forward when seeking backward or forward.

## State and Persistence Behavior

All asset bytes are compiled into the binary. Opened file objects keep per-handle reader position only; no durable or shared mutable state is written.

## Dependencies and Integration Points

`dlna.go` serves `/static/` from `data.Assets`; `data.go` reads `rootDesc.xml.tmpl` from it. The embedded SCPD XML must match service handlers.

## Risks and Test Signals

This generated code should not be manually edited. Risks are stale asset generation, unusual generated identifier characters, seek behavior over gzip, and mismatch between embedded XML and handlers. Tests that fetch `rootDesc.xml` and static service links indirectly validate availability.
