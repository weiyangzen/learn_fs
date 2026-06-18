# sources/sync-backup/git-lfs/tr/trgen/trgen.go

Purpose: generator that embeds compiled `.mo` translation files into Go source.

Important APIs/types/functions: `infof`, `warnf`, `readPoDir`, `verbose` flag, and `main`.

Control flow: searches root candidates for `po/build`, exits successfully if missing, creates `tr/tr_gen.go`, writes package/init boilerplate, scans `.mo` filenames with regex, reads each file, base64-encodes content into `locales[...]`, and reports count in verbose mode.

State and persistence: writes generated Go file and reads translation build artifacts.

Dependencies and integration points: invoked by `go generate` directive in `tr.go`; produced file populates `locales` map used by `InitializeLocale`.

Risks: regex only accepts letters, hyphen, and underscore locale names. Output file is partially written if an error occurs mid-generation. Missing `po/build` is treated as success.

Test signals: no direct tests in this subset.
