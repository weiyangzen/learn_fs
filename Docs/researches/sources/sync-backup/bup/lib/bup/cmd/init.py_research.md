# sources/sync-backup/bup/lib/bup/cmd/init.py

## Purpose
`init.py` creates a local or remote bup repository. It is the command-line entry for repository initialization through the unified repository location abstraction.

## APIs and Control Flow
`main(argv)` parses optional `-r/--remote` and at most one directory. A positional directory becomes a `file` URL with an absolute path and cannot be combined with `--remote`. Otherwise `main_repo_location` resolves the target. `repo_for_location(loc, create=True)` performs the actual initialization inside a context manager.

## State, Dependencies, Integration, Risks, Tests
The persistent effect is a new bup/git repository at the selected location. Dependencies include `URL`, `main_repo_location`, `repo_for_location`, `argv_bytes`, and `git.GitError`. Risks are ambiguous local-vs-remote target selection, poor diagnostics if remote creation fails, and filesystem permission errors. Test signals include positional/remote conflict, multiple-argument rejection, absolute local path conversion, remote path parsing, successful context open, and `EXIT_FAILURE` on `GitError`.
