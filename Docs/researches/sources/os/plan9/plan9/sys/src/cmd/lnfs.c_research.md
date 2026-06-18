# File Research: sources/os/plan9/plan9/sys/src/cmd/lnfs.c

Read fully: 781 lines, 13332 bytes. SHA-256 prefix: `15660ed50240b787`.

This is a user-level 9P filesystem that overlays a directory and maps long or space-containing names to short filesystem-safe names. It mounts over a mountpoint, serves 9P requests over a pipe, and maintains `./.longnames` as the translation database. Long names are shortened to the first `NAMELEN-1` bytes of base32-encoded MD5.

9P handlers include version, attach, walk, open, create, read, write, clunk, remove, stat, and wstat. Directory reads translate short names back to long names. Creates and wstats translate long names to short names, adding entries to `.longnames` when writable. `readnames()` refreshes the translation cache based on `.longnames` qid/length.

Integration: uses Plan 9 `fcall`, `String`, `libsec` MD5/base32, mount/srv posting, and local filesystem syscalls.

Risk notes: explicitly no authentication. `-r` enforces read-only behavior for creates/writes/wstats and namefile mutation. Fid state is manually managed and reused.
