# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/vac.c

Purpose: main Vac archive creation command.

Command behavior:
- Supports archive mode (`-a`), output file (`-f`), diff archive (`-d`), merge mode, quick diff, stdin input, exclusions, block size selection, Venti host selection, verbose output, and stats.
- Creates a new Vac filesystem or opens an existing archive filesystem for dated snapshots.
- Emits the final `vac:<score>` line after `vacfssync`.

Core flow:
- `threadmain` parses options, connects to Venti, sets up output root, processes stdin and command-line files, records qidspace, syncs, prints root score, and cleans temporary output on failure.
- `recentarchive` finds the newest `yyyy/mmdd[.n]` archive directory for diffing.
- `plan9tovacdir` maps Plan 9 `Dir` metadata into `VacDir`.
- `vac` recursively archives files/directories, applies include/exclude filters, creates Vac nodes, copies metadata, and writes data.
- With a diff archive, unchanged blocks are skipped by comparing SHA1 block scores; quick diff can skip whole files based on metadata.
- `vacmerge` and `vacmergefile` merge existing `.vac` roots while offsetting qid ranges to avoid collisions.
- `vacstdin` archives standard input under a supplied name.
- `unittoull` parses size suffixes.

Integration points:
- Relies heavily on `file.c` APIs and `glob.c`.
- Uses Venti connection setup and packet stats.
- Archive mode depends on the dated tree layout and root previous-score linkage.

Risks:
- The code intentionally relies on content-addressed block reuse for diffing and merging; incorrect block size assumptions can reduce reuse.
- `vacmerge` expects qidspace metadata or falls back to max-qid discovery; qid range maintenance is a key invariant.
- `removevacfile` only removes `vacfile`, so archive-file creation cleanup is limited to non-archive `-f` output.
