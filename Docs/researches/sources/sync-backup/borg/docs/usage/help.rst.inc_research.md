# sources/sync-backup/borg/docs/usage/help.rst.inc

Purpose: generated help-topic include covering patterns, archive matching, placeholders, and compression.

Important APIs and control flow: pattern help defines `fm:`, `sh:`, `re:`, `pp:`, and `pf:` styles; include/exclude pattern file prefixes `R`, `P`, `-`, `!`, and `+`; first-match ordering; and command-line/file precedence. Archive matching supports name/id shell/regex/exact, `aid:`, user, host, and tags. Placeholders include hostname, fqdn, reverse-fqdn, now/utcnow with strftime, user, pid, and Borg version parts. Compression specs include none, lz4, zstd, zlib, lzma, auto, and obfuscate padding.

State and persistence: no direct state, but these topics define how archives are selected, files are included/excluded, archive names/comments are generated, and chunks are compressed.

Dependencies and integration points: Python fnmatch/re/string/datetime formatting, pattern engine hashtable path-full matching, create/extract/export/diff filters, archive filters, systemd escaping, compression libraries, encryption for obfuscation, and chunk size limits.

Risks: untrusted regex/shell/fnmatch patterns can cause expensive matching. `pf:` ignores context/order due to O(1) lookup. Placeholder percent escaping is tricky in systemd units. Compression obfuscation increases repository size and only makes sense with encryption.

Test signals: pattern precedence fixtures, Windows path conversion/reserved-character behavior, archive matching by every selector, placeholder expansion/escaping, compression spec parsing, and generated examples remaining runnable.
