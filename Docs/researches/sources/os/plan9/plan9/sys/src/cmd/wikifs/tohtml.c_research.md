# File Research: sources/os/plan9/plan9/sys/src/cmd/wikifs/tohtml.c

This file renders parsed wiki documents and histories to HTML or plain text, using templates from the wiki directory.

Template handling:
- Template names include page/edit/diff/history/new/oldpage/werror HTML and selected text templates.
- `gettemplate` caches template contents in per-template RW-locked cache entries.
- The current code has cache freshness checks disabled with `if(0 && ...)`, so it effectively stats/reads more often than the comments imply.

HTML rendering:
- `s_escappend` escapes `<`, `>`, `&`, and optionally turns spaces into newlines outside pre mode.
- `mkurl` preserves absolute URLs and anchors, turns bare email-like strings into `mailto:`, otherwise creates relative wiki links.
- `pagehtml` emits headings with anchors, paragraphs, lists, links, manpage links, pre blocks, horizontal rules, and escaped plain text while managing open block tags.

Diff rendering:
- `s_diff` writes old/new rendered HTML to temporary files, runs `/bin/diff`, and wraps unchanged/changed spans as old/new text.
- `diffhtml` iterates history from newest to oldest and renders each version with metadata and diff to previous version.

History rendering:
- `historyhtml` emits a list of versions with dates, authors, conflict marker, and comments.

Top-level HTML:
- `tohtml` loads a template, substitutes `TITLE`, `VERSION`, and `DATE`, inserts generated `PAGE` content according to template type, and appends remaining template.

Plain text rendering:
- `pagetext` serializes `Wpage` nodes back to wiki text, optionally prefixing lines with `#` for history storage.
- Handles headings, paragraphs, bullets, links, man refs, pre blocks, rules, wrapping around 70 runes, and indentation prefixes.
- `historytext` renders version list.
- `totext` mirrors `tohtml` for text templates.
- `doctext` emits metadata plus serialized page body.

Notable risks:
- `s_diff` depends on external `/bin/diff` and temporary files.
- HTML link text in headings is not escaped in all paths.
- Template cache code comments do not match the disabled freshness checks.
