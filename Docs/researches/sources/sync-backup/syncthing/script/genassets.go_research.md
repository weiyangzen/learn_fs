# Research: sources/sync-backup/syncthing/script/genassets.go

## sources/sync-backup/syncthing/script/genassets.go

Purpose: generates Go source embedding static assets into an `assets.Asset` map.

Important APIs/types/functions: template `tpl`, `asset`, `templateVars`, `walkerFor`, and `main` with `-o` output flag.

Control flow: walks the input directory, skips dotfiles, reads regular files, gzip-compresses each and keeps the gzipped payload only when smaller, records original length and slash-normalized relative name, renders a Go source template, formats it with `go/format`, and writes to stdout or output file.

State and persistence: output is generated Go code. The generated modification time is current Unix time or `SOURCE_DATE_EPOCH` for reproducible builds.

Dependencies and integration: standard library plus `lib/assets` in the generated code. Risks include embedding binary data as quoted strings, no sorting before template output, ignored walk/template write errors in some paths, and reproducibility depending on stable walk order. Test signal is generated code compilation and asset-serving behavior.
