# sources/sync-backup/borg/.github/workflows/codeql-analysis.yml Research

## Purpose

`codeql-analysis.yml` runs GitHub CodeQL semantic analysis for BorgBackup's C/C++ and Python code. It scans pushes and pull requests affecting code and runs a scheduled weekly scan.

## Important APIs, Types, and Functions

Triggers include pushes to `master`, pull requests to `master`, and a Friday cron. Path filters include Python, Cython, C, C headers, and the workflow itself. The `analyze` job runs on `ubuntu-24.04`, times out after twenty minutes, grants `security-events: write`, and uses a matrix over `cpp` and `python`. Steps check out full history, set up Python 3.11, cache pip, install native packages, initialize CodeQL with `github/codeql-action/init@v4`, build/install Borg in a venv, and run `github/codeql-action/analyze@v4`.

## Control Flow

For each language matrix item, the job provisions dependencies, initializes CodeQL for that language, builds Borg so compiled extensions and source context are available, and uploads analysis results through the CodeQL action.

## State and Persistence Behavior

The workflow creates temporary virtual environments and pip cache entries on the runner. CodeQL results are uploaded as security alerts/results to GitHub. It does not modify repository files.

## Dependencies and Integration Points

It integrates with GitHub CodeQL, GitHub security-events permissions, Borg's locked development requirements, native build dependencies (`libssl`, `libacl`, `liblz4`), setuptools-scm full-history needs, and Python/C++ build tooling.

## Risks and Edge Cases

Twenty minutes may be tight if dependency installation or analysis slows. CodeQL action versions are tag-pinned rather than SHA-pinned. Path filters omit docs and other configuration, which is appropriate for analysis but means some build-affecting non-code changes may not run CodeQL. The same build step is used for both language matrix entries, which is simple but duplicates work.

## Test Signals

Signals include successful CodeQL workflow completion, uploaded code scanning alerts, cache hit rates, and build/install success before analysis. A code change in both Python and C should trigger two matrix entries.
