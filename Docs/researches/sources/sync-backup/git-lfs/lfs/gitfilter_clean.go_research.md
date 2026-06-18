# sources/sync-backup/git-lfs/lfs/gitfilter_clean.go

Purpose: implements the Git clean filter path: convert working-file content into a Git LFS pointer and store content in a temp file for later object storage.

Important APIs/types/functions: `cleanedAsset`, `GitFilter.Clean`, `copyToTemp`, and `cleanedAsset.Teardown`.

Control flow: `Clean` loads sorted extensions; with extensions, it pipes through them, uses the final output OID and temp file size, and records pointer extensions for changed transformations. Without extensions, `copyToTemp` hashes and copies input to a temp file. `copyToTemp` first tries to decode existing pointer-like input and returns a clean-pointer error for small canonical pointer data to avoid double-cleaning.

State/persistence behavior: writes temp files and returns their names; `Teardown` removes them. Actual LFS object storage happens outside this file.

Dependencies/integration: depends on `DecodeFrom`, pointer encoding, SHA-256, temp-file helpers, extension piping, and progress callbacks.

Risks/test signals: clean-pointer detection depends on `blobSizeCutoff` and partial buffering. Callback is disabled when file size is unknown/nonpositive. Extension results influence pointer extension metadata and must align with smudge verification.
