# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlfmt/html.c

HTML parser adapter and text renderer for `htmlfmt`.

- Reads all input fd bytes into `Bytes`, constructs a `URLwin`, and parses HTML with Plan 9 `parsehtml()`.
- Converts parsed item trees into wrapped plaintext.
- Renders text items, rules, images, form fields, tables, floating items, and spacers.
- Optional `-a` mode emits image/link/form annotations such as `[image URL]` and anchor URLs.
- Builds absolute URLs using a regular expression over schemes and host components.
- Detects charset from an early `<meta ... charset=...>` string, defaulting to ISO-8859-1.

Dependencies are Plan 9 `html.h`, `regexp.h`, draw types, rune conversion helpers, and local `dat.h`.

Notable concerns:
- Charset detection is explicitly a hack and searches only a simple meta/header pattern.
- `rendertext()` comments out freeing `rurl`, leaving a small leak.
- Table rendering flattens cells sequentially rather than preserving layout.
