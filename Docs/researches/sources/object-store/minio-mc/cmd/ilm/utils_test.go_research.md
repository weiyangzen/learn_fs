# Research: sources/object-store/minio-mc/cmd/ilm/utils_test.go

Purpose: unit tests for lifecycle tag display formatting.

Important APIs/types/functions: `TestILMTags`.

Control flow: constructs one rule with a single `RuleFilter.Tag` and another with multiple `RuleFilter.And.Tags`; asserts `getTags` returns `key=value` or `key=value&...` strings.

State and persistence: no persistence.

Dependencies/integration points: standard testing and MinIO lifecycle types.

Risks: only tag formatting is covered. It does not test empty tags, key-only tags, ordering assumptions beyond the configured slice order, or escaping.

Test signals: confirms stable tag string formatting used by ILM list tables.
