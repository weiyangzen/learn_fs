# sources/sync-backup/syncthing/cmd/dev/stcompdirs/main.go

Purpose: development utility that compares multiple directory trees and reports the first content, metadata, symlink, or presence mismatch.

Important APIs/types/functions: `compareDirectories`, `fileInfo`, `startWalker`, and `sha256file`. `fileInfo` captures relative name, mode, modification time, and SHA-256 hash; symlink hash is the link target, directories omit hash and mtime.

Control flow: `main` parses positional dirs and logs `compareDirectories`. One walker goroutine per directory sends sorted `filepath.Walk` results through a channel. The comparator reads one item from each channel, compares against the first directory, aborts other walkers on errors or mismatches, and returns nil only when all walkers finish together.

State and persistence behavior: read-only filesystem traversal. Transient state is channels, abort signal, and SHA-256 hashes.

Dependencies/integration: uses standard library filesystem APIs. It ignores `.stversions` and `.stfolder`, aligning with Syncthing folder internals.

Risks/test signals: `filepath.Walk` ordering is lexical on most platforms but comparison assumes walkers advance in matching order. Hash read errors abort. Signal is nil for identical trees and clear missing/mismatch errors for divergent trees.
