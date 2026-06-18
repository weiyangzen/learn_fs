# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/chk.c

Filesystem consistency checker and optional repair tool for cwfs. It walks dentries recursively, validates tags/qids/block ownership, audits or rebuilds free lists, and can repair bad tags/blocks or clear temporary files.

Important behavior:
- Console entry is `cmd_check`.
- Options include `rdall`, `tag`, `pfile`, `pdir`, `free`, `ream`, `bad`, `touch`, `trim`, and `rtmp`.
- Tracks allocated/free/qid bitmaps and reports duplicate, missing, bad, and out-of-range blocks.
- `fsck()` recursively checks direct and indirect blocks, directory contents, names, qids, and temporary files.
- `mkfreelist()` rebuilds normal free lists; `trfreelist()` preserves/free-list-translates cache-worm devices.
- `xtag()` validates block tags and can reset them under selected repair flags.
- Locks `mainlock` for writable checking and disables aging during scans.
