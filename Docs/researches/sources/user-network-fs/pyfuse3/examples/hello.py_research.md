## sources/user-network-fs/pyfuse3/examples/hello.py

Purpose: Minimal Trio-based pyfuse3 filesystem example exposing a single read-only file `message`.

Important APIs/types/functions: `TestFs` implements `getattr`, `lookup`, `opendir`, `readdir`, `open`, and `read`; `init_logging`, `parse_args`, and `main` handle CLI and pyfuse3 lifecycle.

Control flow: `main` parses mountpoint/debug options, initializes `TestFs`, sets FUSE options, calls `pyfuse3.init`, runs `trio.run(pyfuse3.main)`, and closes on normal or exceptional exit. Filesystem methods map root and one file inode to static attributes/data.

State and persistence: In-memory only: fixed inode/name/data and deterministic timestamps. No underlying filesystem writes.

Dependencies and integration: Demonstrates `pyfuse3.Operations` with Trio, FUSE entry attributes, file handles, and `readdir_reply`.

Risks and test signals: It rejects writes and unknown names; exceptions close without unmount. Tests can mount in a temp mountpoint, read `/message`, list root, try write/open errors, and run with debug options.
