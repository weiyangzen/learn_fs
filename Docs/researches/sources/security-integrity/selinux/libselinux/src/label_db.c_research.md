# sources/security-integrity/selinux/libselinux/src/label_db.c

Purpose: Implements the database-object labeling backend, primarily for SE-PostgreSQL-style object names.

Important APIs/types/functions: `selabel_db_init()` installs `db_close`, `db_lookup`, and `db_stats`. `spec_t` contains lookup record, wildcard key, database object type, and match count. `process_line()` maps strings like `db_table`, `db_column`, and `db_procedure` to `SELABEL_DB_*` constants.

Control flow: initialization parses `SELABEL_OPT_PATH` or default `selinux_sepgsql_context_path()`, verifies a regular file, grows a flexible `catalog_t` array while reading lines, ignores malformed/comment-only lines with warnings, records digest, and stores `rec->spec_file`. Lookup scans in file order for matching type and `fnmatch()` key.

State and persistence: per-handle catalog persists until close; match counts support stats. No config is modified.

Dependencies and integration: frontend handles validation/translation; backend depends on path helpers, `fnmatch`, and database label constants.

Risks and test signals: lookup order is first-match, so spec file ordering matters. Tests should cover every type string, wildcard matching, malformed lines, non-regular files, catalog growth, digest, and stats counts.
