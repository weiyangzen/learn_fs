# File Research: sources/os/bsd/netbsd-src/lib/libc/time/zic.c

## Purpose
Implements `zic`, the timezone compiler that reads tzdb `.zi` source files and optional leap-second files, then emits TZif timezone files and links under the target timezone directory.

## Main Entry Points
- `main()` parses command-line options, reads leap and timezone input files, associates rules with zones, changes into the output directory, emits each zone, creates links, and handles `localtime`/`posixrules` compatibility links.
- `infile()` reads input line by line, tokenizes fields, dispatches `Rule`, `Zone`, `Link`, `Leap`, and `Expires` records, and handles zone continuation lines.
- `outzone()` expands a zone’s rules into transition/type tables and calls `writezone()`.
- `writezone()` writes TZif v2/v3/v4 data blocks, including 32-bit and 64-bit sections, leap second tables, type records, abbreviation strings, and the trailing POSIX TZ string.

## Parsing And Data Model
The file models tzdb source records with `struct rule`, `struct zone`, and `struct link`. Rules encode year ranges, month/day selectors, transition time basis, DST save value, and abbreviation variable text. Zones encode standard offset, rule reference or fixed save value, format string, continuation end time, and associated rule slices. Links are collected and sorted before filesystem creation.

Parsing helpers include `getfields()` for comments, whitespace, and quoted fields; `gethms()`/`getsave()` for offsets and DST-save parsing; `rulesub()` for year/month/day/time rule fields; `getleapdatetime()`/`inleap()`/`inexpires()` for leap records; and `namecheck()` for portable zone/link names.

## TZif Generation
`outzone()` computes a bounded year range from referenced rules, leap years, truncation options, bloat mode, and POSIX string availability. It materializes transition instants with `rpytime()`, chooses time types with `addtype()`, builds abbreviations with `doabbr()` and `addabbr()`, and optionally trims trailing transitions that can be represented by the POSIX TZ footer.

`writezone()` sorts and merges transitions, applies leap-second corrections, truncates data using `-r`/`-R`, creates a 32-bit range and full 64-bit range, decides when TZif v4 is required, remaps/omits unused types, writes headers in network byte order, emits transitions/types/leaps/std-wall/ut-local indicators, then appends the POSIX string.

## Filesystem Behavior
Output uses randomized temporary names via `random_dirent()` and `open_outfile()`, then atomically renames with `rename_dest()`. Directory creation is handled by `mkdirs()` unless `-D` disables it. `dolink()` tries hard links, then symlinks with relative target synthesis, then byte-for-byte copies. Link creation detects duplicate link names, self-links, chains, and cycles.

## Options And Compatibility
Supports `-b slim|fat`, `-d`, `-D`, `-g`, `-l`, `-L`, `-m`, `-p`, `-r`, `-R`, `-t`, `-u`, `-v`, plus ignored historical `-s`/`-y`. “Fat” output preserves older-client compatibility behavior; “slim” may omit redundant 32-bit content and transition tails. Verbose mode emits compatibility warnings for older zic/TZif consumers.

## Dependencies
Depends on NetBSD libc/toolchain configuration, `private.h`, `tzfile.h`, POSIX file APIs, optional `getrandom`, gettext, `setmode/getmode`, pwd/group lookup, symlink/hardlink support, signal handling, and tzdb constants such as `TZ_MAX_TYPES`, `TZ_MAX_CHARS`, `TZ_MAGIC`, and calendrical macros.

## Risks And Notes
The code is global-state heavy: parsed rules/zones/links, transition arrays, leap arrays, output options, diagnostics, and abbreviation tables are process globals. Correctness depends on overflow-checked arithmetic (`oadd`, `tadd`, `omul`), careful handling of leap-second truncation, correct std/wall/UT transition conversion, and preserving legacy TZif behavior for old readers. Link handling is intentionally defensive because link targets may themselves be links or unavailable until later passes.
