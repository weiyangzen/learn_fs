# File Research: sources/virtualization/virtiofsd/src/server.rs

## Purpose

This file implements virtiofsd’s FUSE protocol server. It decodes incoming FUSE request messages from guest memory, dispatches them to a generic `FileSystem` implementation, and encodes FUSE replies. It also adapts descriptor-backed I/O to zero-copy filesystem traits and forwards serialization hooks for migration.

## Main Types And Constants

- `FUSE_BUFFER_HEADER_SIZE`: additional inbound size allowance for the FUSE header area.
- `MAX_BUFFER_SIZE`: maximum local request/reply data buffer, 1 MiB.
- `DIRENT_PADDING`: zero padding for 8-byte aligned directory entries.
- `CURRENT_DIR_CSTR`, `PARENT_DIR_CSTR`: special directory entry names used by `READDIRPLUS`.
- `ZcReader<'a>`: wraps descriptor `Reader` as `ZeroCopyReader`.
- `ZcWriter<'a>`: wraps descriptor `Writer` as `ZeroCopyWriter`.
- `Server<F>`: generic FUSE server over a `FileSystem`; stores the filesystem and negotiated FUSE options in an `AtomicU64`.

## Top-Level Dispatch

`Server::handle_message()` reads an `InHeader`, rejects oversized inbound messages, converts the opcode with `Opcode::try_from`, logs request metadata, and dispatches to one method per FUSE opcode.

Implemented dispatch includes lookup, forget, getattr, setattr, readlink, symlink, mknod, mkdir, unlink, rmdir, rename, link, open, read, write, statfs, release, fsync, xattrs, flush, init, opendir, readdir, releasedir, fsyncdir, locking stubs, access, create, interrupt, bmap, destroy, ioctl, poll, notify reply, batch forget, fallocate, readdirplus, rename2, lseek, copy file range, setup/remove mapping stubs, syncfs, and tmpfile stub.

Unknown opcodes return `ENOSYS`.

## Request Handling Pattern

Most handlers follow the same pattern:

1. Read the typed FUSE input structure with `Reader::read_obj()`.
2. Compute remaining variable-length bytes using checked subtraction from `in_header.len`.
3. Read names or payloads into a vector.
4. Convert NUL-terminated names with `bytes_to_cstr()`.
5. Convert `InHeader` into filesystem `Context`.
6. Call the corresponding `FileSystem` method.
7. Return either `reply_ok(...)` or `reply_error(...)`.

This pattern is used for metadata operations, namespace operations, file handles, xattrs, and directory handles.

## Zero-Copy I/O

`ZcReader` implements `ZeroCopyReader::write_to_file_at()` by repeatedly writing from guest descriptors into a host file at the requested offset until count is exhausted, a zero write occurs, or checked arithmetic fails.

`ZcWriter` implements `ZeroCopyWriter::read_from_file_at()` by repeatedly reading from a host file into guest descriptors at the requested offset. Both wrappers protect against offset wrap-around and impossible count underflow.

`read()` splits the reply writer after the `OutHeader` and passes a `ZcWriter` to `fs.read()`. It then writes a custom `OutHeader` whose length includes the actual byte count. `write()` passes a `ZcReader` to `fs.write()` and replies with `WriteOut`.

## Initialization And Negotiation

`init()` reads `InitInCompat`, optionally reads `InitInExt` when `INIT_EXT` is offered, validates protocol major/minor versions, and declares supported FUSE options. Supported defaults include async read, parallel directory ops, big writes, auto invalidation, async DIO, ioctl directory support, atomic truncate, max pages, submounts, init extensions, create supplementary groups, and idmap support.

The effective enabled options are `capable & (want | supported)`, where `want` comes from `fs.init(capable)`. The selected option bits are stored in `self.options`.

The reply sets max background, congestion threshold, max write, nanosecond time granularity, page count, and split 64-bit flags.

## Directory Handling

`readdir()` asks `fs.readdir()` for a `DirectoryIterator`, writes dirents with `add_dirent()`, stops cleanly when the buffer is full, and replies with the actual byte count.

`readdirplus()` additionally resolves each non-`.`/`..` dirent through `fs.lookup()` using `handle_dirent()`, then writes `EntryOut` plus `Dirent`. If the buffer fills or an error occurs after a lookup, it calls `fs.forget(..., nlookup = 1)` to avoid lookup count leaks. If no entries have been written, the first error is returned.

`handle_dirent()` creates synthetic negative entries for `.` and `..` rather than looking them up.

`add_dirent()` strips the trailing NUL from the name, computes aligned dirent length, checks for overflow, writes optional `EntryOut`, writes `Dirent`, writes the name, and pads to 8-byte alignment. It returns `Ok(0)` when the caller’s remaining buffer cannot fit the complete entry.

## Extended Request Extensions

`get_extensions()` parses create-like request extensions after the filename when negotiated options require them. It supports:

- `SECURITY_CTX`: parsed by `parse_security_context()`, currently allowing at most one security context.
- `CREATE_SUPP_GROUP`: parsed by `parse_sup_groups()` into guest GIDs.

It validates extension header sizes, rejects truncated payloads, rejects duplicate or unsupported extensions, and requires a security context when the feature was negotiated. Supplementary groups are optional because the kernel only sends them when needed.

`parse_sup_groups()` enforces `LINUX_NRGROUPS_MAX`, verifies exact padded size, and decodes `u32` GIDs into `GuestGid`.

A unit test verifies that a truncated supplementary-groups extension is rejected with `EINVAL`.

## Reply Helpers

- `reply_readdir(len, unique, w)`: writes a successful `OutHeader` for directory replies and flushes.
- `reply_ok(out, data, unique, w)`: writes a successful header, optional fixed object, and optional byte payload.
- `reply_error(e, unique, w)`: writes an error header using negative errno, defaulting to `EIO`.
- `strerror(error)`: formats errno names for debug logging.
- `bytes_to_cstr(buf)`: validates NUL termination and absence of interior NULs.
- `take_object<T>()`: unaligned decode of a `ByteValued` object from a byte slice.

## Unsupported Or Stubbed Operations

`setupmapping()` and `removemapping()` return `ENOSYS`.

`getlk`, `setlk`, `setlkw`, `bmap`, `ioctl`, `poll`, and `notify_reply` defer to filesystem methods that may themselves return unsupported errors.

`tmpfile()` expects `fs.tmpfile()` to return an error and panics if it unexpectedly succeeds, then returns that error.

`interrupt()` and `destroy()` produce no FUSE reply; `destroy()` calls `fs.destroy()` and clears negotiated options.

## Serialization Integration

`impl SerializableFileSystem for Server<F>` forwards `prepare_serialization`, `serialize`, and `deserialize_and_apply` to the wrapped filesystem. This is used by `vhost_user.rs` migration handling.

## Integration Points

This file is the bridge between:

- `descriptor_utils::{Reader, Writer}` for guest descriptor access.
- `fuse::*` for protocol structures, flags, opcodes, and reply layouts.
- `filesystem::*` for the backend filesystem abstraction.
- `soft_idmap::GuestGid` for supplementary group extension decoding.
- `passthrough::util::einval` for EINVAL construction.
- `vhost_user.rs`, which calls `Server::handle_message()` for each vring descriptor chain and calls serialization methods during migration.

## Important Invariants

- Variable-length request sizes are computed with checked arithmetic to avoid underflow.
- Xattr, directory, and batch-forget sizes are bounded by `MAX_BUFFER_SIZE`.
- Names must be valid C strings with a single trailing NUL.
- Directory entries must be 8-byte aligned.
- `READDIR` and `READDIRPLUS` may return less than requested rather than failing large output sizes.
- `READDIRPLUS` must balance lookup counts when it cannot return an entry it already looked up.
- Negotiated options are stored atomically and affect later parsing of create/xattr extension layouts.

## Risks And Edge Cases

- Many handlers allocate vectors sized by guest-controlled message lengths after validation; missed checks would be high risk.
- Some unsupported operations return success with zero bytes if the filesystem stub returns `Ok(())`; behavior depends on the `FileSystem` trait implementation.
- `tmpfile()` panics if a filesystem reports success even though the server treats the operation as unsupported.
- `take_object()` uses unaligned reads from arbitrary bytes but only for `ByteValued` types.
- Protocol changes in Linux FUSE extension layout must be mirrored in `get_extensions()`.
