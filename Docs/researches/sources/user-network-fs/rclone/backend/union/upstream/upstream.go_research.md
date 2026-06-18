# sources/user-network-fs/rclone/backend/union/upstream/upstream.go

Purpose: wraps real rclone filesystems/entries with union-specific root, permission, usage-cache, and writeback metadata.

Important APIs: `Fs`, `Directory`, `Object`, `Entry`; `New`, `Prepare`, wrapping helpers, permission helpers, `Put`, `PutStream`, object `Update`, optional metadata/tier/id/mime proxies, `Writeback`, `About`, `GetFreeSpace`, `GetUsedSpace`, `GetNumObjects`, and usage refresh internals.

Control flow/state: `New` parses remote specs and suffixes `:ro`, `:nc`, `:writeback`, resolves cached root/rooted filesystems, and pins them. Usage cache refresh runs synchronously once, later in background, with expiry in `atomic.Int64`. Writes optimistically adjust cached usage.

Dependencies/integration: union `common`, rclone `fs/cache/fspath/operations`, and standard sync/atomic/time packages. Policies query permission and usage; union object open uses writeback.

Risks/test signals: `Object.Update` computes `delta` but adjusts usage by old size, risking cached accounting errors. Background `cacheUpdate` is lightly synchronized. Unsupported usage metrics use sentinel values that affect policy decisions.
