# File Research: sources/local-fs/xfsdump/restore/dirattr.h

## Role

`dirattr.h` declares the public interface for the directory-attribute registry implemented by `dirattr.c`. The registry lets restore code save directory metadata during the directory dump phase and retrieve/apply it later.

## Public Types and Constants

- `typedef size32_t dah_t`: opaque handle for a registered directory attribute record.
- `DAH_NULL`: sentinel handle meaning no directory attributes have been registered.

The handle is intentionally abstract. Callers should not interpret it as an offset or index.

## Lifecycle API

- `dirattr_init(char *housekeepingdir, bool_t resync, uint64_t dircnt)`
  - Creates or reopens the registry in the housekeeping directory.
  - `resync` means resume an existing context.
  - `dircnt` is a sizing hint for fresh initialization.
- `dirattr_cleanup(void)`
  - Removes backing files and in-memory state.

## Directory Attribute API

- `dirattr_add(filehdr_t *fhdrp)`
  - Registers directory metadata from a dump file header and returns a `dah_t`.
- `dirattr_update(dah_t dah, filehdr_t *fhdrp)`
  - Replaces metadata for an existing handle.
- `dirattr_del(dah_t dah)`
  - Declared as a free/delete operation, but implementation is currently a no-op.
- Getter functions retrieve mode, uid, gid, atime, mtime, ctime, XFS xflags, extsize, project ID, DM event mask, and DM state.
- `dirattr_flush(void)`
  - Flushes buffered registry writes.

## Directory Extended Attribute API

- `dirattr_addextattr(dah_t dah, extattrhdr_t *ahdrp)`
  - Associates an extended attribute record with a directory handle.
- `dirattr_cb_extattr(dah_t dah, cbfunc, ahdrp, ctxp)`
  - Iterates all extended attributes associated with a handle.
  - Stops and returns false if the callback returns false.

The callback receives an `extattrhdr_t *` whose name/value payload follows the header according to the dump format.

## Utility Declaration

- `create_filled_file(const char *pathname, off64_t size)`
  - Declared here for shared use, though implemented in `dirattr.c`.
  - Creates a file and tries to reserve the requested size.

## Usage Contract

Callers must initialize the registry before adding or retrieving handles, treat `DAH_NULL` as invalid for getters, and call `dirattr_flush()` before relying on all buffered records being present on disk. The API is tightly coupled to xfsrestore dump structures (`filehdr_t`, `extattrhdr_t`) and restore-local types.
