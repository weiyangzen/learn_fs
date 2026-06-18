# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/fs.c

9p filesystem front end for a file-backed wiki. It maps wiki page titles and numeric ids into directories containing rendered HTML/text, raw current data, edit pages, history, diffs, and historical revisions.

Key behavior:
- Qid paths encode type, page number, page version index/time, and file index.
- Root exposes `new`, `map`, and one directory per wiki page title; title lookup accepts numeric ids or normalized names.
- First-level page directories expose `index.html`, `index.txt`, `current`, `history.html`, `history.txt`, `diff.html`, `edit.html`, `werror.html`, `werror.txt`, `.httplogin`, plus second-level history directories named by revision timestamp.
- Second-level history directories expose only current-style rendered/text/raw files for that revision.
- Walking a file pre-renders the requested content into fid-local `String` storage using `tohtml`, `totext`, `doctext`, or `.httplogin` loading.
- Opening root captures a map snapshot for directory reads; opening page directories refreshes history/current document state.
- `new` is writable and accumulates a full raw wiki page until a zero-length write finalizes parsing, title allocation, conflict checking, and `writepage()`.
- Writing `map` resolves a page name to a numeric id for later reads.
- `main()` validates the wiki directory, initializes the map, optionally starts network listeners, and posts/mounts the service.

Notable dependencies:
- lib9p, wiki parser/formatter/cache APIs from `wiki.h`, Plan 9 auth/listen support.

Research notes:
- Writes use the attaching user name as author unless overridden by raw `A` metadata; network listener identity may be appended.
- `new` finalization uses a zero-length write as the commit signal.
