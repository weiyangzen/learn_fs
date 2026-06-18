<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/pycheckpatch -->
# sources/user-network-fs/nfs-ganesha/src/scripts/pycheckpatch

## Purpose
`pycheckpatch` runs the repository's Linux-style `checkpatch.pl` against one or more Git commits. It accepts normal `git rev-list` arguments and optionally checks all commits with `-a`; without `-a`, it stops at the first failing commit.

## Important APIs, Types, and Functions
The script has no reusable functions beyond a local Python 2.6-compatible `subprocess.check_output` shim. Important variables are `checkpatch = "./src/scripts/checkpatch.pl"`, `rev_list_args`, `check_all`, and `result`, a list of `(commit, passed, output)` tuples. External command APIs are `git rev-parse --show-toplevel`, `git rev-list --no-merges`, and `git show <commit> --format=email | checkpatch.pl -`.

## Control Flow
The script validates that at least one revision argument is present, removes `-a` if supplied, changes to the Git top-level directory, expands commits with `git rev-list --no-merges`, and exits if the range is empty. It then streams each commit as email-format patch text into `checkpatch.pl`. Failures are recorded; if the failure is the known missing `.checkpatch.conf` message, the script exits with setup guidance. Otherwise it breaks after the first failure unless `-a` was requested, then prints an aggregate pass/fail summary.

## State and Persistence Behavior
The only state is in memory and process current working directory. It reads Git history and checkpatch configuration but writes no files. Exit status is zero only if every checked commit passed.

## Dependencies and Integration Points
It depends on Python, Git, `src/scripts/checkpatch.pl`, and the repository's `.checkpatch.conf` setup. It is part of developer and CI review tooling, complementing `runcp.sh`, Gerrit checkpatch scripts, and pre-commit hooks.

## Risks and Test Signals
Risks include Python 2/3 byte-string mismatches because `subprocess.check_output` returns bytes on Python 3 while string comparisons use text, shell injection if commit identifiers were untrusted, assumptions about running from a checked-out repository, and no handling for merge commits by design. Test signals include empty ranges, a known-good single commit, a failing commit with and without `-a`, missing `.checkpatch.conf`, and execution under both Python 2-compatible and Python 3 interpreters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/pycheckpatch -->
