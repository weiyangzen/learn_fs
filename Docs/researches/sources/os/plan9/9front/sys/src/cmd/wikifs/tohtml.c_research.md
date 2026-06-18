# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/tohtml.c

Renderer for wiki pages, histories, diffs, edit text, and raw document text in HTML and plain text.

Key behavior:
- Template names map to HTML and text templates; templates are cached in `cache[]` with qid/time fields, though the time/qid fast paths are currently disabled by `if(0)`.
- `pagehtml()` emits headings, paragraphs, lists, links, man-page links, preformatted blocks, rules, and escaped plain text.
- `mkurl()` turns relative wiki links into parent-relative paths, supports absolute URL schemes, email auto-mailto, and old-page relative paths.
- `diffhtml()` and `s_diff()` render revision diffs by writing old/new HTML to temp files, running `/bin/diff`, and marking old/new spans.
- `historyhtml()` and `historytext()` list revisions with timestamps, authors, conflict markers, and comments.
- `tohtml()` and `totext()` splice rendered page/history/diff/edit/error content into templates, substituting `TITLE`, `VERSION`, and `DATE`.
- `pagetext()` converts parsed nodes back to wiki source, with optional leading `#` for history-file bodies and wrapping around 70 runes.
- `doctext()` serializes a `Wdoc` as wiki history metadata plus body.

Notable dependencies:
- Plan 9 String library, Bio, `/bin/diff`, temp files from `util.c`, wiki data types.

Research notes:
- The man-page HTML links point to the historical Bell Labs Plan 9 man2html URL.
- HTML escaping in non-pre text turns spaces into newlines.
