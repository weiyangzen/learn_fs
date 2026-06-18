# sources/sync-backup/rsync/testsuite/unsafe-links_test.py

Purpose: end-to-end symlink policy test for default archive behavior, `--copy-links`, and `--copy-unsafe-links`.

Important APIs and flow: creates `from/safe/files`, `from/safe/links`, and `from/unsafe`, with two safe relative links and one unsafe `../../unsafe/unsafefile` link. Default `rsync -avv from/safe/ to` must copy all three as symlinks. `--copy-links` must materialize all as regular files. `--copy-unsafe-links` must leave safe links as symlinks but materialize the unsafe one. The unsafe-copy scenario is repeated from a changed CWD and from an absolute source path.

State and persistence: operates under `TMPDIR`, manually removes `to` between scenarios, and uses helper assertions for symlink target and regular-file existence.

Dependencies and integration: integrates flist symlink classification, `unsafe_symlink()`, copy-link options, and relative/absolute source normalization. Risks include pre-existing `TMPDIR/from` if harness cleanup changes. Test signal distinguishes link preservation from dereferencing by both file type and symlink target text.
