<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.c -->
# sources/security-integrity/selinux/mcstrans/src/mcstrans.c

## Purpose

Core mcstrans translation engine. It parses `setrans.conf` and included `.d` files, builds domains, base classifications, modifier groups, constraints, regexes, and bounded raw/trans caches, then translates SELinux MLS/MCS ranges in both directions. The source was read completely for this report (2209 lines).

## Important APIs, Types, and Functions

Exports `init_translations()`, `finish_context_translations()`, `trans_context()`, and `untrans_context()`. Important internal types include `domain_t`, `base_classification_t`, `word_group_t`, `word_t`, `context_map_t`, and sensitivity/category constraint nodes. Key helpers parse raw MLS levels, category bitmaps, config lines, includes, constraints, cache entries, PCRE2 regexes, and computed raw/trans strings.

## Control Flow

Configuration flow: `init_translations()` requires MLS enabled, reads `selinux_translations_path()`, and `process_trans()` handles `Domain`, `Include`, `Base`, `ModifierGroup`, `Whitespace`, `Join`, `Prefix`, `Suffix`, `Default`, constraints, direct cache mappings, and group words. Translation flow extracts a context range, checks caches, computes full or split range translations, updates caches, and rewrites the context range using libselinux context APIs.

## State and Persistence Behavior

Persistent-on-daemon state is in static globals: linked-list domains, constraints, parser cursor fields, `maxbit`, per-domain hash tables, compiled PCRE2 expressions, and cache entry counts capped by `CACHE_MAX_ENTRIES`. `finish_context_translations()` tears down domains, constraints, bitmaps, regexes, and parser state.

## Dependencies and Integration Points

Depends on libselinux context/path APIs, libsepol MLS ebitmap helpers, PCRE2, glob includes, syslog, and local `mls_level` helpers. It is called by `mcstransd` and by command-line utilities through `mcstrans.h`.

## Risks and Edge Cases

High-risk areas include config parser permissiveness, glob include recursion, category bounds (`MAX_CATS`, `maxbit`), PCRE2 pattern construction from config text, cache consistency between raw/trans tables, split range mutation/restoration, and memory cleanup on allocation failures. Translation semantics are sensitive to group ordering and Hamming-distance word selection.

## Test Signals

Signals include `mlstrans-test`, `try-all`, example configuration round-trips, daemon SIGHUP reload checks, cache hit/miss smoke tests, malformed config tests, and ASan/Valgrind runs over init/translate/finish cycles.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/mcstrans/src/mcstrans.c -->
