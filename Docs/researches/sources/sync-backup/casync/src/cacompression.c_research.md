# sources/sync-backup/casync/src/cacompression.c

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.c -->
## sources/sync-backup/casync/src/cacompression.c

Purpose: `cacompression.c` maps casync compression enum values to user-facing strings and parses strings back to enum values.

Important APIs and functions: a static `table` maps `CA_COMPRESSION_XZ` to `"xz"`, `CA_COMPRESSION_GZIP` to `"gzip"`, and `CA_COMPRESSION_ZSTD` to `"zstd"`. `ca_compression_type_to_string` bounds-checks an enum and returns a string or `NULL`. `ca_compression_type_from_string` rejects empty input, treats `"default"` as `CA_COMPRESSION_DEFAULT`, otherwise scans the table and returns a matching enum or invalid.

Control flow: parsing is linear over `_CA_COMPRESSION_TYPE_MAX`. Formatting is direct table lookup after range checks.

State and persistence: no mutable state. These conversions influence CLI/config/protocol-facing representation but do not persist anything themselves.

Dependencies and integration points: depends on `cacompression.h` and utility helpers `isempty` and `streq`. It integrates with chunk load/save code, command-line option parsing, and build-time compression feature selection.

Risks: the table contains strings for all enum values even if the corresponding library was not built. Callers must still check build support before attempting compression. Empty or null strings return invalid. The default mapping depends on compile-time `HAVE_LIB*` macros, so behavior changes across builds.

Test signals: tests should parse each string, format each valid enum, reject unknown/empty strings, and verify `"default"` maps to the build-selected default.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacompression.c -->
