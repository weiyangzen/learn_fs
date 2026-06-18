# sources/sync-backup/git-lfs/t/t-ls-files.sh

## Purpose

Comprehensive coverage for `git lfs ls-files`. It validates normal, debug, size, long OID, name-only, JSON, include/exclude, checkout/download status, subdirectory invocation, case sensitivity, index-vs-tree behavior, historical refs, `--all`, deleted files, invalid argument ordering, escaped Unicode paths, reference ranges, and independence from fetch filters.

## Important APIs, control flow, and dependencies

The tests initialize many repos, use `git lfs track`, commit/add/remove tracked files, mutate working tree and `.git/lfs/objects`, run `git lfs ls-files` with flags (`--debug`, `--size`, `--include`, `--exclude`, `--all`, `--deleted`, `--name-only`, `--json`, `--long`), compare exact output with heredocs, and inspect refs/tags/ranges. They also test path filter cache settings via `lfs.pathFilterCacheSize`.

## State, dependencies, integration points, risks, and test signals

State includes index entries, HEAD trees, historical refs, working-tree file presence, local object cache, `.gitattributes`, path filters, case sensitivity (`core.ignorecase`), deleted entries, and JSON output files. Integration points are pointer scanning from index/tree/history, local object existence checks, checkout status detection, include/exclude filtering, path normalization from subdirectories, Unicode path handling, and output serializers. Risks include mixing index state into historical refs, incorrect `downloaded` flags, duplicate OID collapse hiding duplicate files, path filters affecting `ls-files`, or malformed JSON/order. Signals are exact text diffs, grep counts, line counts, exit-code checks, and JSON heredoc diffs.
