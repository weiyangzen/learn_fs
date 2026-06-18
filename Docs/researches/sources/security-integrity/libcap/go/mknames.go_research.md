## sources/security-integrity/libcap/go/mknames.go

Purpose: generator that converts C `cap_names.h` plus per-capability documentation snippets into the Go package's `names.go`.

Important APIs/functions: flags `--header` and `--textdir`; reads header, extracts quoted capability names, reads `<textdir>/<index>.txt`, emits `NamedCount`, Go `Value` constants, `names` map, and reverse `bits` map.

Control flow: validates `--header`, scans lines containing quotes from generated C header, for each name reads matching documentation, rewrites `CAP_` references to `cap.`, requires first doc line to start with `Allows `, emits comments and uppercase trimmed constants using `iota`, then emits maps.

State/persistence: writes generated Go source to stdout; `go/Makefile` redirects through `gofmt` to `good-names.go` and diffs against `../cap/names.go`.

Dependencies/integration: Go standard library, generated `libcap/cap_names.h`, `doc/values/*.txt`, and cap package source conventions.

Risks: parser is intentionally simple and depends on exact generated header/doc formats; typo in fatal text does not affect behavior but indicates manual maintenance.

Test signals: `make -C go good-names.go` and diff against committed `../cap/names.go`.
