# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/wrarena.c

`wrarena` reads a standalone arena image and writes its clumps to a Venti server. It caches the arena data in memory, reads clump headers and directory entries directly, decompresses compressed clumps with `unwhack()`, verifies scores/types, then sends clumps through multiple `vtwrite` sender threads.

Options select host, arena offset, max writes, verbose score printing, and disabling libventi double-check SHA1. Host `/dev/null` skips server connection but still walks/verifies clumps.

This is a restore/import utility. It assumes the arena image is locally readable and valid enough for direct in-memory clump/directory indexing.
