# sources/test-tools/syzkaller/pkg/email/patch.go

Purpose: `patch.go` extracts diff content from email text and formats outgoing kernel patch descriptions with tags, recipients, and base commit metadata.

Important APIs/types/functions: `ParsePatch` scans for diff starts and returns normalized diff text. `PatchTemplateData` carries base commit, fixes tag, tools, authors, recipients, links, closes, reported-by, reviewed-by, acked-by, and tested-by fields. `FormatPatchDescription` and `FormatPatch` render outgoing text. `formatAssistedBy`, `diffRegexps`, and `lineMatchesDiffStart` support formatting and parsing.

Control flow and state: `ParsePatch` begins collecting at git/index/new-file/Index diff markers, continues through blank/context/add/remove/hunk/separator lines, and stops at signature separators or quoted reply lines. Scanner `ErrTooLong` suppresses the patch as invalid input; other scanner errors panic because the source is memory. Formatting builds To/Cc `mail.Address` lists, shortens long Fixes hashes to 12 chars, sorts/reverses tool names, prefixes Gemini tool labels, always includes syzbot in `Assisted-by`, and appends `base-commit`.

Dependencies and integration: it depends on `pkg/aflow/ai` recipient/fixes types and Go templates. `parser.go` uses `ParsePatch` for incoming messages; patch-generation flows use formatting helpers.

Risks: scanner default token size rejects very long diff lines. Diff parsing is heuristic and may stop on non-standard lines. Recipient display names are not independently sanitized here. Tests in `patch_test.go` cover many diff styles and formatting outputs.
