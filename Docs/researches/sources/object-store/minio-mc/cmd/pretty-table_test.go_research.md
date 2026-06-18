# Research: sources/object-store/minio-mc/cmd/pretty-table_test.go

## sources/object-store/minio-mc/cmd/pretty-table_test.go

Purpose: verifies core ASCII behavior of `PrettyTable.buildRow`.

Important APIs and functions: `TestPrettyTable` is a table-driven unit test over separators, field definitions, contents, and expected row strings.

Control flow: each test constructs a `PrettyTable`, calls `buildRow`, and fails immediately if the result differs. Cases cover empty table, one unlimited field, one truncated field, ignored separator for a single column, multi-column separator insertion, and mixed truncated/unlimited fields.

State and persistence: test-only, no mutation beyond local variables.

Dependencies and integration: directly protects `pretty-table.go`, which is used by replication and status output.

Risks and test signals: tests use only ASCII strings and max lengths greater than three, so they do not cover Unicode width, colorized output interactions, or negative slice risk when `maxLen < 3`.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/pretty-table_test.go -->
