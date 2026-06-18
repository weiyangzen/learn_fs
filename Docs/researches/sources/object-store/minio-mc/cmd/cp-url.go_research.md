# sources/object-store/minio-mc/cmd/cp-url.go

Purpose: Converts `mc cp` source/target arguments into concrete one-to-one copy jobs.

Important APIs/types/functions: `copyURLsType`, `guessCopyURLType`, `prepareCopyURLsTypeA/B/C/D`, `makeCopyContentTypeA/B/C`, `prepareCopyURLsOpts`, `copyURLsContent`, and `prepareCopyURLs`.

Control flow: The code classifies copy forms: file-to-file, file-to-directory, recursive directory-to-directory, and multi-source-to-directory. It stats sources/targets, verifies directory requirements, prevents copying a directory into itself, recursively lists source contents, constructs target paths, de-duplicates multi-source targets, and applies older/newer time filters.

State and persistence: No persistence; creates streams of `URLs` describing later transfer work.

Dependencies/integration: Depends on `newClient`, `url2Stat`, `firstURL2Stat`, `isAliasURLDir`, `Client.List`, `urlJoinPath`, and time filter helpers.

Risks: Correctness depends on sorted/listing semantics and path separator handling across filesystem and object storage. Recursive copy behavior is sensitive to trailing separators and source prefix trimming.

Test signals: No direct tests in this subset; copy behavior likely covered by integration tests elsewhere.
