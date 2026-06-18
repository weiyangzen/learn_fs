# sources/user-network-fs/rclone/cmd/listremotes/listremotes_test.go

Purpose: unit-tests the filtering semantics for `listremotes`.

Important functions: `resetFilterFlags`, `TestTypeFilterDefaultIsFuzzy`, `TestTypeFilterExactMatchesWholeValue`, and `TestPositionalFilterExactAlsoMatchesWholeValue`. Tests call `compileFilters` and `includeRemote` directly against synthetic `config.Remote` values.

Control flow/state: tests mutate package-level filter globals, then use `t.Cleanup` to reset them. They assert that default matching is case-insensitive non-anchored glob matching while `--exact` matches complete values and still ignores case.

Dependencies/integration: testify assertions and rclone `config.Remote`. Risks are limited to package-global flag leakage if future tests forget cleanup. Test signal is narrow but valuable for a behavior users might misinterpret: `--type box` matching `dropbox` unless `--exact` is supplied.
