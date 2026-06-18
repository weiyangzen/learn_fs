# sources/user-network-fs/go-nfs/nfs_onsymlink.go

## Purpose

`nfs_onsymlink.go` implements the NFSv3 `SYMLINK` procedure handler. It creates a symbolic link inside the filesystem represented by an NFS file handle, applies requested post-creation attributes when the server handler supports mutation, and serializes the NFS success result including the new object handle, post-operation attributes, and weak cache consistency data for the parent directory.

## Important APIs, Types, and Functions

The main API is `onSymlink(ctx context.Context, w *response, userHandle Handler) error`, registered elsewhere as the procedure handler for `NFSProcedureSymlink`. It consumes a `DirOpArg` for parent handle and link name, `ReadSetFileAttributes` for requested link attributes, and `xdr.ReadOpaque` for the symlink target. It depends on the `Handler` interface for `FromHandle`, `ToHandle`, and `Change`, and on helper serializers `WritePostOpAttrs`, `WriteWcc`, and `tryStat`.

## Control Flow

The handler sets `w.errorFmt` to `wccDataErrorFormatter`, decodes request fields in NFS wire order, resolves the parent file handle to a `billy.Filesystem` and path, and rejects stale handles, read-only filesystems, overlong names, existing destination paths, missing or non-directory parents, and filesystem symlink failures with mapped `NFSStatusError` values. After `fs.Symlink(target, newFilePath)` succeeds, it creates an NFS handle for the new path, applies requested attributes via `userHandle.Change(fs)` when available, builds an XDR response with `NFSStatusOk`, a present-object-handle discriminator, the handle, post-op attributes for the link, and WCC data for the parent, then writes the bytes to the response.

## State and Persistence Behavior

The persistent state mutation is the symlink creation in the backing `billy.Filesystem`. Attribute application may further mutate mode, ownership, or times depending on the `Change` implementation. The response includes best-effort post-operation stat data, but no explicit rollback is attempted if attribute application fails after symlink creation. The `ctx` parameter is unused, so cancellation does not interrupt filesystem work.

## Dependencies and Integration Points

This file integrates NFS XDR decoding/encoding (`go-nfs-client/nfs/xdr`), repository NFS status helpers, the repository handler abstraction, and `go-billy` filesystem capability checks. It requires the backing filesystem to advertise `billy.WriteCapability` and implement `Symlink`; filesystems lacking symlink support will surface as `NFSStatusAccess`.

## Risks and Edge Cases

The filename check converts bytes to string and only checks length against `PathNameMax`; path separator or special-name policy depends on the backing filesystem and handler. There is a race between destination `Stat` and `Symlink`, so concurrent creators can still win. Parent pre-operation WCC data is passed as `nil`, reducing cache consistency precision on success. Attribute failure after symlink creation leaves the symlink present while returning an I/O error. Target contents are accepted as an opaque path without normalization or maximum-length enforcement.

## Test Signals

Useful tests should issue real NFS `SYMLINK` calls against writable and read-only billy filesystems, verify returned object handles and link attributes, and cover existing targets, non-directory parents, stale handles, unsupported symlink implementations, overlong names, and attribute mutation failures. Existing integration tests in `nfs_test.go` exercise server/RPC plumbing but do not directly cover this handler.
