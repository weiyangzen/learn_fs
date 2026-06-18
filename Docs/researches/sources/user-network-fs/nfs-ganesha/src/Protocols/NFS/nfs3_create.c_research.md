## sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs3_create.c

Purpose: implements NFSv3 regular file `CREATE`.

APIs and flow: `nfs3_create` prepares result and attr structures, converts parent handle, captures pre-op parent attrs, verifies parent is a directory, checks inode quota, validates the filename, converts create attributes for guarded/unchecked modes, supplies default mode 0600 when absent, maps NFS create mode to FSAL mode, applies verifier for exclusive create, squashes requested owner/group if needed, calls stateless `fsal_open2` with read/write, builds a post-op file handle and attrs, sets WCC data, closes/releases the created object, and releases parent refs. `nfs3_create_free` frees the allocated handle on success.

State/dependencies: mutates namespace and uses FSAL create/open, quota, attr conversion, handle conversion, and WCC helpers.

Risks/tests: test guarded/exclusive/unchecked behavior, verifier semantics, quota denial, bad names, default mode, owner squash, handle allocation/freeing, retryable errors, and parent WCC consistency.
