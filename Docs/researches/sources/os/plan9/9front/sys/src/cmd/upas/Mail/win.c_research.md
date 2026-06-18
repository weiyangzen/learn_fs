# File Research: sources/os/plan9/9front/sys/src/cmd/upas/Mail/win.c

This file abstracts Acme window operations. `wininit()` creates a new window under `/mnt/wsys`, names it, disables scroll, opens `event`, `addr`, and `data`, and creates an `Ioproc` for buffered I/O.

`winevent()` parses Acme event records, including expanded text events, and `winreturn()` writes unhandled events back. The file also provides helpers to open window files, write tags, duplicate data as `Biobuf`, close all descriptors, read arbitrary address ranges with UTF-aware trimming, read/set selections, and match message references in clicked text.

This module is the boundary between mailbox/message/compose logic and Acme’s file interface.
