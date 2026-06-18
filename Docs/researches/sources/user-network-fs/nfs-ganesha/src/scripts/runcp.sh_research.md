<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/runcp.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/runcp.sh

## Purpose
`runcp.sh` is a wrapper around `checkpatch.pl` for checking source files or Git diffs and collecting reports under an output directory. It encodes NFS-Ganesha-specific exclusions and per-file ignored checkpatch classes for generated, external, or historically nonconforming code.

## Important APIs, Types, and Functions
The main functions are `check_one_file`, `check_files`, `check_find`, `check_git_files`, `check_git`, and `show_help`. CLI options control clean-file reporting (`-c`), warning suppression (`-w`), quiet mode (`-q`), per-file reports (`-1`), target directory (`-d`), exclusions (`-x`), inclusion of normally ignored/generated/external files (`-i`, `-e`), Git diff mode (`-g`, `-k`), output directory (`-o`), final report printing (`-r`), typedef ignoring (`-t`), special ignore disabling (`-v`), and cruft filtering (`-K`).

## Control Flow
The script initializes defaults, parses options with `getopts`, normalizes `DIR`, creates the output directory, and initializes `results.cp`, `results.temp`, and `results.err`. It builds an exclusion expression from always-excluded files, generated/config parsing files, and external code unless overridden. `check_find` scans `*.[ch]` files; `check_git` scans `git diff --name-only <commit>`. `check_one_file` decides report paths, applies special `--ignore` switches by matching the file path against configured regexes, runs `checkpatch.pl --file`, and appends interesting output to the aggregate report.

## State and Persistence Behavior
The script writes persistent report files under `ODIR` (default `/tmp/checkpatch`), including `results.cp`, temporary/error files, and optionally one `.cp` file per source. It reads the source tree and Git diff but does not modify source files.

## Dependencies and Integration Points
It depends on `/bin/sh`, `readlink`, `sed`, `egrep`, `grep`, `find`, `sort`, `git`, and `src/scripts/checkpatch.pl`. It integrates with NFS-Ganesha's generated XDR/RPC headers, external libraries, and project-specific checkpatch exceptions.

## Risks and Test Signals
The implementation uses many unquoted variables and legacy backticks, so paths with whitespace or regex metacharacters can misbehave. Several shell constructs assume a forgiving shell; `return` is used at top level in error paths. The exclusion and ignore regexes can mask real style regressions if they become too broad. Test signals include `-g` against a small diff, `-1` per-file output, `-c` and `-w` filters, `-i`/`-e` inclusion toggles, invalid output directory handling, and a file that matches each special ignore class.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/runcp.sh -->
