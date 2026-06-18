# sources/test-tools/syzkaller/pkg/email/patch_test.go

Purpose: `patch_test.go` validates incoming patch extraction and outgoing patch formatting.

Important tests: `TestParsePatch` covers git diffs, index lines, file mode lines, new files, Index-style diffs, multi-file patches, signature and quoted-reply cutoffs, empty input, and realistic kernel patch mail content. `TestFormatPatch` checks rendered descriptions with Fixes, Assisted-by, review/ack/test/report/link tags, signed-off-by lines, To/Cc addresses, base-commit, and tool ordering.

Control flow and state: parse tests are table-driven with expected exact diff strings, including trailing newline normalization. Format tests build `PatchTemplateData` and compare exact output.

Dependencies and integration: tests exercise `ParsePatch`, template rendering, `mail.Address` formatting, AI recipient/fixes types, and assisted-tool normalization.

Risks/test gaps: tests do not explicitly cover scanner-too-long behavior, malformed recipients, or `Closes` output despite template support. They provide strong regression coverage for the common patch shapes seen in mailing-list traffic.
