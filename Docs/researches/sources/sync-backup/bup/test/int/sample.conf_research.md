<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/int/sample.conf -->
# sources/sync-backup/bup/test/int/sample.conf

Purpose: fixture Git config file for `test_git.py` config parsing. Important data keys include `bup.foo=bar`, `bup.bup=is great`, `bup.end=end`, invalid-looking comment keys, boolean-like values, empty values, and integer/hex values. Control flow is declarative; `git.git_config_get()` reads it through Git config semantics during tests. State is static file content only. Dependencies are Git config syntax, including comment parsing and section/key normalization. Risks are accidental formatting changes altering Git's parsed output, especially comments, empty values, boolean aliases, and hex integer conversion. Test signals are `test_config()` assertions that expected keys resolve, invalid bool/int conversions raise `ConfigError`, missing keys return `None`, and typed values parse correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/int/sample.conf -->
