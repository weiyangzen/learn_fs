# File Research: sources/local-fs/reiserfsprogs/Makefile.am

This top-level Automake file defines the reiserfsprogs build subtree order: `include`, `lib`, `reiserfscore`, `fsck`, `debugreiserfs`, `resize_reiserfs`, `mkreiserfs`, and `tune`.

It also declares distribution-only files: `CREDITS`, `version.h`, and `reiserfsprogs.spec`.

Key role: root build orchestration only. No runtime logic.
