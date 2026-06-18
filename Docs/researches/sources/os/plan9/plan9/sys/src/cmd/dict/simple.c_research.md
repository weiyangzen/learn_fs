# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/simple.c

Minimal UTF dictionary backend for one-record-per-line data with headword and entry separated by a tab.

`simpleprintentry` emits bytes until tab/newline/end. In headword mode it stops at the tab; in normal mode it converts the tab to a space and continues until newline. `simplenextoff` reads one newline-delimited record and returns the next offset. `simpleprintkey` reports no key.

Integration points: registered in `utils.c` for Leon Ungier Russian/English dictionaries.

Risks and notes: no escaping or validation; entries cannot contain embedded newlines, and tab is the only headword/body separator.
