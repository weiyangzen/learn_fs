# File Research: sources/os/plan9/9front/sys/src/cmd/git/import

Patch/mail importer implemented in `rc` plus an embedded `awk` parser. It accepts stdin or file paths, including upas message directories with separate `header` and `body`, extracts `From`, `Date`, `Subject`, body text, and diff content, then applies the patch.

`apply1` first dry-runs `patch -np1` to discover affected files and uses `git/walk -q` to reject clobbering dirty files. On success it applies with `patch -p1`, updates tracked/removed files with `git/add`, refreshes walk status, and unless `-n` is supplied creates a commit via `git/save` with author/committer/date/parent metadata. It updates the active ref and appends clean index entries. Multiple patches are delimited by the same `⑨` separator emitted by `git/hist`.
