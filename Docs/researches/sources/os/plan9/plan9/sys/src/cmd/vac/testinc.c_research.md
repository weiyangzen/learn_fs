# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/testinc.c

Purpose: small command-line harness for the Vac include/exclude pattern engine.

Behavior:
- Accepts one include/exclude rules file.
- Calls `loadexcludefile`.
- Reads paths from standard input using `Brdline`.
- Prints `0` or `1` from `includefile(path)` followed by the path.

Integration points:
- Exercises `glob.c` rule loading and matching without running a full archive.
- Uses the same internal headers as `vac.c`.

Risks:
- Input line handling assumes newline-terminated records and overwrites the trailing newline.
