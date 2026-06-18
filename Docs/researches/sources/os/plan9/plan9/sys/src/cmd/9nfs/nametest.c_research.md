# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/nametest.c

Purpose: interactive/test utility for Unix id/name mapping.

Key behavior: reads maps or ids, supports commands to reload maps, translate id-to-name/name-to-id, print current server/client pair, and switch between user/group maps.

Integration notes: depends on `readunixids`, `readunixidmaps`, `pair2idmap`, `id2name`, and `name2id` implemented outside this file group.
