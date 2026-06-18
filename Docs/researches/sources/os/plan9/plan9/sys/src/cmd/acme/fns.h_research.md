# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/fns.h

This header declares cross-module Acme functions and convenience macros.

Key contents:
- Warning/error, plumber, snarf, temp file, scroll, font, command argument, new/undo/cut/paste/get/put/font APIs.
- Window/error-window helpers, command runner, fsys lifecycle, regex/address helpers, text search/expansion helpers.
- Allocation helpers: `emalloc`, `erealloc`, `estrdup`, `runemalloc`, `runerealloc`, `runemove`.
- Generic helpers: `cvttorunes`, `runeeq`, `min`, `max`, rune/byte conversion, whitespace scanners.
- 9P server hooks: `fsysinit`, `fsysmount`, `fsysincid`, `fsysdelid`, `respond`.

Filesystem relevance:
- Connects all Acme modules, including pseudo-filesystem, real-file operations, and buffer loading.
