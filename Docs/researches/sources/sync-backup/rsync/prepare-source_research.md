# sources/sync-backup/rsync/prepare-source

Purpose: Maintainer helper script that either builds generated autoconf files locally or fetches generated/source files from the rsync upstream distribution area.

Important APIs, types, and functions: Shell actions are `build`/`make`, `fetch`, `fetchgen`, and `fetchSRC`. It invokes `packaging/prep-auto-dir`, `make -f prepare-source.mak`, `rsync-ssl`, and filesystem operations to symlink/copy configure inputs.

Control flow: The script determines its directory, optionally switches into a prepared `build` dir, creates symlinks for `configure.ac` and `m4`, copies existing generated files if needed, defaults to `build` when no action is supplied, then tries requested actions in order until one succeeds. Unknown actions fail immediately.

State and persistence behavior: Mutates the working tree or build directory by creating symlinks, copying generated files, touching `configure.sh`/`config.h.in`, and fetching content over rsync. It does not maintain a separate state file.

Dependencies and integration points: Integrates with `prepare-source.mak`, `rsync-ssl`, upstream rsync servers, and the autoconf toolchain. Used by maintainers before releases or source preparation.

Risks and test signals: Risks include destructive replacement of local files/symlinks, reliance on network/upstream layout, and action fall-through semantics that stop at first success. Test signals are running `prepare-source build` in a clean checkout, verifying generated timestamps, and dry-running fetch paths in isolated build directories.
