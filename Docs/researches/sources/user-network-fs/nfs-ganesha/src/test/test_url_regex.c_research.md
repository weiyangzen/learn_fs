# sources/user-network-fs/nfs-ganesha/src/test/test_url_regex.c

Purpose: standalone regex experiment/test for decomposing RADOS object URLs and config URLs.

Important APIs, types, and functions: regexes are `RADOS_URL_REGEX` and `CONFIG_URL_REGEX`. Functions `match_dup`, `split_pool`, and `split_url` duplicate and print matched groups using POSIX regex APIs.

Control flow: `main` compiles the pool/object regex, tests four URL strings, compiles the config URL regex, and tests three quoted/unquoted `rados://` strings. Errors print and exit only on regex compilation failure.

State and persistence: two static `regex_t` objects; heap strings are freed after each match. There is no `regfree`.

Dependencies and integration points: built by test CMake and linked with `ganesha_nfsd`, though it mostly uses libc regex and malloc.

Risks: no assertions or expected-output comparison; it exits 0 even if matching behavior changes. The regexes are permissive and this file may diverge from production parser behavior if production patterns evolve.

Test signals: useful as a manual parser behavior probe. To become a regression test, it should assert captured groups and failure cases.
