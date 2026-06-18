# sources/sync-backup/rsync/rsync-web/convert-gpl

Purpose: Perl filter that converts GPL/plain text snippets into simple HTML-safe output for the website.

Important APIs, types, and functions: Reads stdin line by line, escapes `&`, `<`, and `>`, converts a form-feed character to `<hr>`, hyperlinkifies bracketed `http`/`https` URLs, and prints transformed lines.

Control flow: Linear streaming transformation in a `while (<>)` loop.

State and persistence behavior: Stateless filter; output is written to stdout and no files are changed directly.

Dependencies and integration points: Depends on Perl. Intended for rsync-web content generation.

Risks and test signals: Risks include incomplete HTML sanitization for URLs inserted into `href`, regex greediness, and limited markup semantics. Tests should feed text with special characters, form feeds, multiple URLs, and already-escaped content.
