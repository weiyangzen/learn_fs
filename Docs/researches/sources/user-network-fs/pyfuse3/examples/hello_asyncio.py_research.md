## sources/user-network-fs/pyfuse3/examples/hello_asyncio.py

Purpose: Asyncio variant of the minimal pyfuse3 single-file example, also showing termination via xattr.

Important APIs/types/functions: Enables `pyfuse3.asyncio`, implements the same `TestFs` methods as `hello.py`, plus `setxattr` accepting `command=terminate` on the root inode to call `pyfuse3.terminate`.

Control flow: `main` initializes FUSE and runs `asyncio.run(pyfuse3.main())`. Filesystem operations serve static root/file metadata and content; unsupported xattrs return `ENOTSUP`, invalid command values return `EINVAL`.

State and persistence: In-memory only with static file content and timestamps.

Dependencies and integration: Demonstrates pyfuse3 asyncio integration, FUSE xattr handling, and graceful event-loop termination.

Risks and test signals: The terminate control path is intentionally exposed through xattr and should be used only for example/test mounts. Tests should cover reading `message`, read-only open enforcement, xattr terminate, and cleanup after exceptions.
