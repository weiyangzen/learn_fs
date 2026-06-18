# sources/object-store/minio-mc/cmd/common-methods.go

## Purpose

`common-methods.go` contains cross-command helpers for deciding whether a URL is directory-like, opening source streams, writing/copying targets, preserving metadata, choosing S3 server-side copy versus streaming upload, and constructing clients from aliases.

## Important APIs, Control Flow, And State

`isAliasURLDir` stats a target when possible, then falls back to alias expansion and trailing-separator heuristics. `getSourceStreamMetadataFromURL`, `getSourceStreamFromURL`, and `getSourceStream` expand aliases, apply SSE keys, and call `Client.Get`. `putTargetRetention`, `putTargetStream`, `putTargetStreamWithURL`, and `copySourceToTargetURL` wrap target client operations with retention/legal-hold metadata. `filterMetadata` drops invalid HTTP headers and server-encryption headers. `getAllMetadata` merges source metadata with target user metadata during preserve flows.

`uploadSourceToTargetURL` is the central copy/upload decision tree. It computes source/target aliases and SSE keys, applies retention/legal hold overrides, merges metadata, uses server-side copy when source and target aliases match, zip/checksum constraints allow it, and otherwise streams from source to target. It also parses multipart size/thread settings from options or env, updates progress totals for streaming readers, copies tags, and chooses `io.LimitReader` when the source is not seekable. `newClientFromAlias` selects filesystem or S3 client based on alias config; `newClient` rejects raw HTTP URLs without an alias.

## Dependencies, Integration, Risks, And Tests

Persistent state is remote/local data changed through the selected client plus environment-controlled multipart settings. Dependencies include alias expansion, SSE lookup, URL structs, `minio-go` tags/retention types, `httpguts`, humanize parsing, progress bars, and shared errors. Risks are metadata mutation through maps, retention handling short-circuiting uploads, server-side copy eligibility tied only to alias equality, nonseekable stream length handling, and process env parsing. Coverage is indirect through copy, S3, filesystem, and STS tests.
