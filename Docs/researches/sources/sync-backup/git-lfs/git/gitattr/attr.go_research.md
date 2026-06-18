# sources/sync-backup/git-lfs/git/gitattr/attr.go

Purpose: parser for `.gitattributes` line syntax, producing typed pattern and macro lines plus attribute key/value state. It also records dominant input line ending so attribute files can be rewritten consistently elsewhere.

Important APIs/types/functions: `Line`, `PatternLine`, `MacroLine`, `Attr`, `ParseLines`, `lineEndingSplitter`, `ScanLines`, and `LineEnding`. `Attr` models true values, `-attr` false values, `key=value`, and `!attr` unspecified resets.

Control flow: `ParseLines` scans trimmed lines, skips blanks and comments, handles quoted patterns via `strconv.Unquote`, recognizes `[attr]` macro definitions, splits attributes on spaces, and constructs either `patternLine` with a `wildmatch.Wildmatch` configured for Git attributes or `macroLine`. Scanner errors and unbalanced quotes are returned.

State/persistence behavior: no durable writes. Parser state is local to the scan except line-ending counters; the returned line-ending string is `\r\n`, `\n`, or empty depending on observed input.

Dependencies/integration: depends on `github.com/git-lfs/wildmatch/v2`, Git LFS localized errors, and is consumed by `MacroProcessor`, `Tree`, and attribute file discovery in `files.go`.

Risks/test signals: syntax support is intentionally simple and space-split; quoted patterns are supported but escaped attribute values are not. Tests cover multiple attributes, comments, unset/unspecified attributes, quoted patterns, bad quotes, no-attribute lines, and macro lines.
