# sources/user-network-fs/rclone/cmd/listremotes/listremotes.go

Purpose: implements `rclone listremotes`, listing configured remotes from config files and environment definitions with filtering, sorting, long output, and JSON output.

Important APIs: filter globals (`filterName`, `filterType`, `filterSource`, `filterDescription`, `exactMatch`), output globals (`listLong`, `jsonOutput`, `orderBy`), `compileFilters`, `includeRemote`, `newLess`, and Cobra `commandDefinition`. `lessFn` composes multi-column stable sorting over `config.Remote`.

Control flow: optional positional filter applies to all attributes; named filters are converted with `filter.GlobStringToRegexp`; `config.GetRemotes` returns remotes; matching remotes are compacted in-place, optionally sorted, then printed as JSON array, tabular long rows, or `name:` lines.

State/persistence: reads rclone config/environment remote registry but does not modify it. Package globals represent flag values. Dependencies include `fs/config`, `filter`, JSON, regexp, sort. Risks include globals in unit tests, glob-vs-exact semantics, and JSON streamed manually rather than through an encoder. Test signal covers fuzzy/exact type and positional filters.
