# File Research: sources/os/plan9/plan9/sys/src/9/port/chan.c

This file is the core Plan 9 channel, path, namespace, mount, and name-resolution implementation.

Key responsibilities:
- Allocates, recycles, references, closes, and asynchronously clunks `Chan` objects.
- Manages `Path` objects with copy-on-write strings and mount-point ancestry.
- Initializes and shuts down all devices in `devtab`.
- Implements reference helpers, kernel string helpers, and name validation.
- Implements mount table operations through `Mhead` and `Mount`: `cmount`, `cunmount`, `findmount`, `domount`, and `undomount`.
- Implements `walk`, including mount crossing, union traversal, `..` handling, and all-or-nothing walk semantics.
- Implements `namec`, the central path-to-channel resolver for bind, mount target, directory, access, open, create, and remove modes.
- Handles create/open race behavior so concurrent `create(2)` calls preserve expected Plan 9 semantics.
- Enforces attach restrictions for `#` device paths under `noattach`.

Important implementation details:
- Paths remember mount points in `Path.mtpt` so `..` can uncross mounts correctly.
- `namec` starts from root, current directory, or a `#` device attach depending on the first path character.
- `validname0` protects against malicious user-space strings by optionally duplicating before rescanning.
- Union directories are handled by trying additional mount elements when a walk fails.
- `ccloseq` defers expensive close operations to `closeproc`.

Filesystem/storage relevance:
- This is the central VFS/namespace file for Plan 9.
- Every local, remote, synthetic, and storage-backed file access flows through channels and path resolution implemented here.
