# sources/user-network-fs/rclone/backend/filelu/filelu_object.go

Purpose: This file implements FileLu object lookup, download, update, removal, hashing, and basic object metadata methods.

Important APIs and types: `Object` stores `fs`, `remote`, `size`, and `modTime`. Methods include `Fs.NewObject`, `Object.Open`, `Object.Update`, `Object.Remove`, `Object.Hash`, `String`, `Fs`, `Remote`, `Size`, `ModTime`, `SetModTime`, and `Storable`.

Control flow: `NewObject` joins root and remote, resolves a file code by listing the parent, fetches file info, parses size, and returns an object. `Open` gets a direct link and size, decodes range/seek options, performs a full HTTP GET to the direct link, optionally discards bytes to reach the offset, and wraps the body with `io.LimitReader` for count-limited reads. `Update` selects simple upload or multipart upload based on `upload_cutoff`, then updates cached size and modtime. `Hash` supports MD5 only if it can infer a file code from the root or a 12-character code in parentheses in the remote name.

State and persistence behavior: Object metadata is cached locally but often uses `time.Now()` rather than provider modtime. Updates create or replace remote files. Removal deletes the remote file by full path. Direct-link downloads update the cached size.

Dependencies and integration points: It calls FileLu client helpers, upload helpers, raw HTTP client, rclone range/seek options, and hash interfaces.

Risks: Range reads are client-side skips over a full direct-link response rather than server Range requests, so large offsets are inefficient. Hash availability is path-shape dependent and not aligned with `Fs.Hashes`. `NewObject` loses provider modtime. Multipart upload is selected solely by size and assumes known positive sizes. `SetModTime` is unsupported.

Test signals: Generic `fstests` exercise normal object lifecycle; invalid UTF-8 is skipped by `filelu_test.go`.
