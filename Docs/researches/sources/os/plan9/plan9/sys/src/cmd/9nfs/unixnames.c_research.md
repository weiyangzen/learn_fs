# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/unixnames.c

Unix user/group identity mapping support for 9nfs.

Key responsibilities:
- Maps a server/client-IP pair to a `Unixidmap` by matching server and client domain regexes.
- Caches successful server/client-IP-to-map lookups in `Unixscmap`.
- Reads the main Unix map configuration, optionally executing lines beginning with `!`.
- Tracks stale map entries and clears their loaded user/group lists when config entries disappear.
- Reloads Unix id files when their timestamp indicates they changed.
- Converts between Unix names and numeric ids with move-to-front list caching.
- Reads passwd/group-style files in Plan 9-style (`3:tom:...`) or Unix-style (`name:*:uid:gid:...`) formats.
- Reuses freed `Unixid` nodes through a free list.

Dependencies:
- Uses `strparse`, `system`, `strstore`, `regcomp`, `regexec`, `getdom`, `dirstat`, `Bopen`, and `Brdline`.
- Shares `Unixidmap`, `Unixmap`, `Unixid`, and `Unixscmap` definitions from 9nfs headers.

Notable risks:
- Regexes are compiled from configuration strings without additional anchoring except explicit full-match checks.
- `checkunixmap` compares `u->timestamp > dir->mtime`, so equal timestamps trigger reload.
- Global lists are not locked.
