# File Research: sources/os/plan9/9front/sys/src/cmd/git/hist

Small `rc` wrapper that prints per-commit history for one or more paths. It calls `git/log -s` with optional `-n`, resolves each commit's parent with `git/query $h~`, and diffs each requested file between parent and commit through the mounted `git/fs` object tree. Missing old or new file versions are mapped to `/dev/null`, so additions and removals are represented as unified diffs.

The output is mail-patch-like: hash, date derived from the commit message file mtime, author, message, file diffs, and a `⑨` separator. This format is intentionally compatible with `git/import`'s parser.
