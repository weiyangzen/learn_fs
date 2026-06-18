# sources/object-store/minio/cmd/metacache-walk.go

Purpose: This file implements per-disk directory walking for metacache listings and exposes it over local storage wrappers and remote grid streams. It is the disk-side producer of sorted `metaCacheEntry` streams consumed by `listPathRaw`.

Important APIs and types: `WalkDirOptions` specifies bucket, base directory, recursive mode, not-found reporting, one-level `FilterPrefix`, `ForwardTo`, limit, and disk ID. `(*xlStorage).WalkDir` performs the actual filesystem traversal. Wrappers `(*xlStorageDiskIDCheck).WalkDir`, `(*storageRESTClient).WalkDir`, and `(*storageRESTServer).WalkDirHandler` add disk-health tracking and remote transport.

Control flow: `xlStorage.WalkDir` validates the volume and access, creates a small-block `metacacheWriter`, and streams entries through a channel. It first handles the S3-specific case where a slash-suffixed base path may itself be a directory object. `scanDir` lists directory entries, filters by prefix and forward marker, reads `xl.meta` or legacy `xl.json`, emits object entries immediately, collects possible directory entries, sorts them, emits directory markers in lexical order, and recurses when requested. It stops early on context cancellation or object limit.

State and persistence behavior: The walker reads object metadata from the disk layout but does not mutate storage. Runtime state includes object count for limit enforcement, directory-object tracking, stack of directories to emit, temporary buffers, and optional walk locks. The remote client serializes `WalkDirOptions` with msgp and streams bytes from a grid handler into the caller's writer.

Dependencies and integration points: It depends on `xlStorage` filesystem helpers, metadata files (`xl.meta`, legacy `xl.json`), volume access checks, disk health tracking, `grid.HandlerWalkDir`, `grid.WriterToChannel`, and the metacache stream writer. It integrates directly with `StorageAPI.WalkDir` calls from `listPathRaw`.

Risks: Correct ordering is subtle because object-vs-directory detection requires metadata reads after directory listing. Concurrent object rewrites can produce EOF or unexpected EOF while reading metadata; the code logs and skips these cases. Prefix and forward handling are lexical and conservative. Legacy filesystem support and `isDirEmpty` behavior vary by filesystem type. Disk ID mismatches must be handled to avoid reading from a replaced drive.

Test signals: This file has generated serialization tests for `WalkDirOptions` but no focused unit test for `xlStorage.WalkDir` in this subset. Practical signals come from listing integration tests: sorted output, recursion, directory objects, limit enforcement, not-found behavior, legacy metadata, disk-health accounting, and remote grid streaming.
