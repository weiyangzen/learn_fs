# sources/sync-backup/bup/lib/bup/cmd/fuse.py

## Purpose
`fuse.py` mounts a bup repository VFS as a read-only FUSE filesystem using the `python-fuse` bindings, exposing repository paths to ordinary file tools.

## APIs and Control Flow
Import-time checks reject missing, fusepy-like, or too-old FUSE modules. `BupFs` implements `getattr`, `readdir`, `readlink`, `open`, and `read`. These methods convert FUSE string paths to argv bytes, resolve VFS items, augment metadata as requested, and stream file reads from `vfs.fopen`. `main(argv)` parses mount options, opens `LocalRepo`, configures foreground/debug/allow-other flags, and starts FUSE.

## State, Dependencies, Integration, Risks, Tests
The mount is read-only and persistent only while the process runs. It depends on `python-fuse`, `vfs`, `xstat`, metadata availability, and byte/path conversion. Risks include the file comment's known path handling limitations because FUSE paths are strings, incomplete offset support in `readdir`, fake metadata defaults unless `--meta` is supplied, and exposing repository content to other users with `--allow-other`. Test signals are import/version rejection, read-only enforcement, symlink reads, metadata times floored to seconds, and directory entry encoding.
