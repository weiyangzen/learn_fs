# File Research: sources/os/plan9/9front/sys/src/cmd/acme/xfid.c

Handles Acme’s 9P request operations for window files and global files such as index/log/cons. It translates file operations on `/mnt/acme` into text edits, selections, control commands, and event traffic.

Important behavior:
- `xfidopen`, `xfidclose`, `xfidread`, and `xfidwrite` implement per-qid behavior for `addr`, `data`, `xdata`, `body`, `tag`, `ctl`, `event`, `rdsel`, `wrsel`, and edit output files.
- Writes to `addr` parse Acme address syntax and update `w->addr`; reads from `data` advance Rune positions.
- `fullrunewrite` preserves incomplete UTF-8 sequences across write calls.
- `xfidctlwrite` parses control commands such as `lock`, `unlock`, `clean`, `dirty`, `name`, `font`, `dump`, `delete`, `del`, `get`, `put`, `dot=addr`, `addr=dot`, `limit=addr`, `nomark`, `menu`, `noscroll`, `cleartag`, and `scratch`.
- `xfideventread` blocks until window events arrive or a flush/delete wakes it.
- `xfidindexread` synthesizes Acme’s global window index.

The critical invariants are window locking, Rune/UTF byte boundary handling, and preserving shared-file state across cloned windows.
