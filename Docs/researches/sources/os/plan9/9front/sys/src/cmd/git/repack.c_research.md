# File Research: sources/os/plan9/9front/sys/src/cmd/git/repack.c

Repository repacker. It lists all refs, writes one new pack containing objects reachable from those refs, indexes it, renames temporary pack/index files to `<packhash>.pack` and `<packhash>.idx`, then removes all loose objects and all older pack files.

The cleanup is aggressive: it removes every loose object directory entry and every pack/index not prefixed by the newly written pack hash.
