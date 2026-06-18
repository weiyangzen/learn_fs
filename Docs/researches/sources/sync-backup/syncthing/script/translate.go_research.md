# Research: sources/sync-backup/syncthing/script/translate.go

## sources/sync-backup/syncthing/script/translate.go

Purpose: extracts GUI translation strings from HTML/JS and merges them into an existing translation JSON.

Important APIs/functions: regexps for Angular translate attributes and `$translate.instant`, `generalNode`, `inTranslate`, `isTranslated`, `translation`, `walkerFor`, `collectThemes`, and `main`.

Control flow: reads existing translation JSON into a nested map, walks GUI files, parses HTML nodes and JS lines, records explicit translate text/ids, logs suspicious untranslated text nodes or data-content strings, adds theme names for GUI theme directories, then writes pretty JSON to stdout.

State and persistence: updates only in-memory translation map and writes JSON output; caller decides file replacement.

Dependencies and integration: `golang.org/x/net/html`, GUI template conventions, Angular translation syntax. Risks include regex-based JS extraction, deprecated `strings.Title`, nested map type assertions, and warning exceptions going stale. Test signal is output JSON diff and translation warning logs.
