# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/util/subst.conf.in

Purpose: `subst.conf.in` is the configuration template consumed by `subst` to map placeholder names to configured build values.

Important APIs, types, and functions: contains substitution keys for tools (`AWK`, `SED`), directories (`ET_DIR`, `SS_DIR`, `datarootdir`, `datadir`, `root_sysconfdir`, `$root_prefix`, `$prefix`), e2fsprogs version/date (`E2FSPROGS_MONTH`, `E2FSPROGS_YEAR`, `E2FSPROGS_VERSION`), C type sizes, and `JDEV`.

Control flow: no executable flow. During configuration, `@...@` tokens are expanded; later `subst.c` reads the resulting file and uses whitespace-separated key/value pairs.

State and persistence: generated config data persists in the build tree and drives later template expansion.

Dependencies and integration points: depends on Autoconf results and is consumed by `util/subst`. `$prefix` and `$root_prefix` keys intentionally support `${prefix}`-style substitution because `subst.c` stores names with `$` prefix for brace expansion.

Risks: blank `JDEV` intentionally disables documentation text; accidental whitespace or comments in values can be truncated by `subst.c`. Values containing `#` are not safe because the parser strips comments.

Test signals: configure substitution followed by generating representative manpages/headers. Verify both `@E2FSPROGS_VERSION@` and `${prefix}` style placeholders resolve.
