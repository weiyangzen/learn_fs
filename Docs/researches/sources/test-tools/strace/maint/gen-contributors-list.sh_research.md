# sources/test-tools/strace/maint/gen-contributors-list.sh

Purpose: produces a unique contributor list for a commit range, optionally including email addresses and optionally merging additional contributors from stdin.

Important APIs/types/functions: `get_commit_id`, `git describe`, `git log`, sed regexes for trailer-like author lines, `git check-mailmap`, sorting, and options `-e/--include-email`, `-/--stdin`, `LAST_COMMIT`, `FIRST_COMMIT`, and `--initial`.

Control flow: parse options, resolve the upper commit and lower bound tag/commit/root, choose output regex based on email inclusion, collect matching names from `git log` and optional stdin, normalize through mailmap, sort unique, and strip or retain email addresses.

State and persistence behavior: no writes; relies on repository history and `.mailmap` state. Output ordering is locale-controlled through `LC_COLLATE=C`.

Dependencies and integration points: called by `gen-tag-message.sh` for release notes and can be used manually for credits. It depends on commit message formatting conventions.

Risks: regex only recognizes specific indented contributor line forms and may miss nonstandard trailers. `--help` exits with status 1, which is unusual for help paths.

Test signals: generated release contributor blocks should match expected mailmap-canonical names for a release range; stdin mode should add normalized extra contributors.
