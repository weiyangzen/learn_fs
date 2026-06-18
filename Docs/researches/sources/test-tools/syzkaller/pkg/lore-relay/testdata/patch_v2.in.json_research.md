## sources/test-tools/syzkaller/pkg/lore-relay/testdata/patch_v2.in.json

Purpose: JSON fixture for rendering a versioned patch email.

Important data: includes patch metadata such as version, subject, recipients, body, and trailer-related fields.

Control flow: consumed by `templates_test.go` to verify subject versioning and body formatting.

State and persistence: static test input.

Dependencies and integration: tied to dashboard poll-result schema and embedded templates.

Risks: fixture needs updates when template policy or API fields change.

Test signals: protects `[PATCH ... v2]` style subject/body rendering.
