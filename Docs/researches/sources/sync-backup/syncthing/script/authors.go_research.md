# Research: sources/sync-backup/syncthing/script/authors.go

## sources/sync-backup/syncthing/script/authors.go

Purpose: maintenance generator that updates `AUTHORS` and the GUI contributor list from repository history.

Important APIs/types/functions: `author`, `authorSet`, `getAuthors`, `addAuthors`, `filteredAuthors`, `stringSet`, and regexps for nicknames, emails, and bots.

Control flow: reads existing `AUTHORS`, scans tracked source-relevant files via `git ls-tree`, runs `git log --follow` per file, records authors and co-authors while skipping known bad commits, filters bot/zero-commit entries, sorts by logarithmic commit bucket then name, rewrites `aboutModalView.html`, and rewrites `AUTHORS`.

State and persistence: writes two repository files. Commit sets are in-memory and keyed by email.

Dependencies and integration: depends on Git, AUTHORS format, and the GUI HTML marker `id="contributor-list"`. Risks include expensive per-file history scans, fragile HTML regexp replacement, email alias merging edge cases, and bot filtering misses. Test signal is mostly review of generated diffs.
