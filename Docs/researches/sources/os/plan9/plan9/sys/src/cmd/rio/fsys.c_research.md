# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/fsys.c

Read status: complete, 700 lines.

`fsys.c` implements `rio`’s 9P filesystem server. It exposes window files such as `cons`, `consctl`, `cursor`, `kbdin`, `label`, `mouse`, `screen`, `snarf`, `text`, `wdir`, `wctl`, `window`, and `wsys`.

`filsysinit` creates close-on-exec pipes, posts `/srv/riowctl.*` and `/srv/rio.*`, starts the wctl and filesystem processes, and records the current user. `filsysproc` reads 9P messages, decodes them, allocates an `Xfid`, finds or creates fids, and dispatches through the `fcall` table.

`filsyswalk` handles ordinary directory entries and `wsys/<id>` window directories. Directory reads synthesize Plan 9 `Dir` records with `dostat`, including sorted window ids for `/dev/wsys`.

Unsupported operations such as create, remove, wstat, and auth are denied. Version negotiation sets the global 9P message size.

Filesystem relevance: central implementation of `rio`’s window namespace.
