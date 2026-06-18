# File Research: sources/os/plan9/9front/sys/src/cmd/sed.c

Purpose: Plan 9 stream editor implementation.

Major components:
- Fixed command storage `pspace[MAXCMDS]`, text buffer `addspace`, line/hold buffers, label table, file cache, and output file table.
- Address model supports none, `$`, line number, regexp, and last regexp.
- `main`: parses `-e`, `-f`, `-g`, `-n`, `-u`, and ignores Unix compatibility `-E`/`-r`; compiles scripts; enrolls input files; executes.
- `fcomp`: compiles sed commands, addresses, blocks, labels, branches, substitutions, transliterations, append/change/insert text, read/write files.
- Regex support: `compile`, `match`, and Plan 9 `regexp.h`.
- Execution: `execute`, `executable`, and `command` apply commands to pattern/hold space.
- Substitution: `substitute`, `dosub`, `place` handle global substitutions, zero-length matches, `&`, and back references.
- I/O: `gline` concatenates enrolled input streams, supports implicit final newline, `$` detection, and unbuffered flush callback.
- Pending output: `arout` processes append/read queues after each cycle.

Integration: Standalone command using Plan 9 Bio, rune, and regexp APIs.

Risks:
- Fixed-size limits include command count, line size, append buffer, labels, files, and subexpressions.
- Uses global mutable interpreter state.
- `ycomp` allocation size depends on highest rune in source set.
- `putline` always appends newline, matching sed pattern-space semantics.
