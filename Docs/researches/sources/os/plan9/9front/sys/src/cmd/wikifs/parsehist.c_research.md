# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/parsehist.c

Parser for wiki history/current files.

Key behavior:
- Reads the first line as the page title.
- Subsequent metadata lines use leading `D` for timestamp, `A` for author, `C` for comment, and `X` for conflict marker.
- Body lines are prefixed with `#`; `Brdwline()` strips the leading `#` and feeds them to `Brdpage()`.
- Builds a `Whist` with an array of `Wdoc` revisions, current revision index, title, document count, and reference count.
- The current index tracks the most recent non-conflicting revision.

Notable dependencies:
- `Brdpage()` from `parse.c`, page freeing from `io.c`, and Plan 9 Bio/String/thread support.

Research notes:
- If parsing any revision body fails, the partially built history is freed and nil is returned.
