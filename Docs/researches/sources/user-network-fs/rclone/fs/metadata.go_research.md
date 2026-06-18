# sources/user-network-fs/rclone/fs/metadata.go

## Purpose
`metadata.go` defines rclone's generic metadata map type and helpers for reading, merging, option injection, and external metadata mapping. It standardizes how operations pass object metadata between backends.

## Important APIs, types, and functions
Exports are `Metadata`, `MetadataHelp`, `MetadataInfo`, methods `Set`, `Merge`, `MergeOptions`, `GetMetadata`, and `GetMetadataOptions`. Internal `mapItem` defines the JSON contract for mapper programs, and `metadataMapper` runs the configured external mapper command.

## Control flow
`GetMetadataOptions` returns nil unless global `Metadata` is enabled. It reads metadata from a `Metadataer` object when available, merges any `MetadataOption` open options, and optionally calls `metadataMapper`. The mapper builds a JSON object with source/destination fs identifiers, remote, size, MIME type, modtime, directory flag, optional ID, and metadata; sends it to stdin; reads JSON from stdout; and returns the output metadata.

## State and persistence behavior
Metadata maps are in-memory. The external mapper can have arbitrary side effects, but this code only starts a subprocess and passes JSON. Config controls whether metadata and mapper execution are active. Dump flags can log mapper input/output.

## Dependencies and integration points
It depends on core interfaces `DirEntry`, `Metadataer`, `IDer`, `Fs`, `OpenOption`, `MetadataOption`, `MimeType`, config `MetadataMapper`, and OS command execution. Backends use these helpers in Put/Update/Copy paths.

## Risks and edge cases
Mapper execution is synchronous and can be slow, fail, or emit invalid JSON. Metadata is merged with options after reading object metadata, so options override duplicate keys. `mapItem.IsDir` is always false in this function despite accepting `DirEntry`, which may matter for directory metadata. Error messages include stderr and stdout snippets.

## Test signals
`metadata_test.go` covers map set/merge semantics, open-option merge precedence, normal mapper transformation, mapper failure via stderr/exit, and option-overridden mapper input.

Source-read signal: reviewed complete local file (172 lines). Types observed: `Metadata`, `MetadataHelp`, `MetadataInfo`, `mapItem`. Functions/methods observed: `Set`, `Merge`, `MergeOptions`, `GetMetadata`, `metadataMapper`, `GetMetadataOptions`.
