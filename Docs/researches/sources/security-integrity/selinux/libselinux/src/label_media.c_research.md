# sources/security-integrity/selinux/libselinux/src/label_media.c

Purpose: Implements a simple media-context labeling backend keyed by media names.

Important APIs/types/functions: `selabel_media_init()` installs close, lookup, and stats callbacks. `spec_t` stores key, lookup record, and match count. `process_line()` parses `<key> <context>` lines.

Control flow: init selects `SELABEL_OPT_PATH` or `selinux_media_context_path()`, verifies a regular file, performs two passes to count and populate specs, records digest, and generates the hash. Lookup scans for exact key match or `*` fallback and increments match count.

State and persistence: per-handle array of specs and match counters persists until close.

Dependencies and integration: frontend handles validation/translation. Backend uses path helpers, digest helpers, and logging.

Risks and test signals: first-match ordering and wildcard fallback determine security labels. Tests should cover empty file, malformed lines, wildcard fallback, regular-file validation, digest generation, and stats.
