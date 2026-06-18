## sources/test-tools/syzkaller/pkg/lore-relay/templates.go

Purpose: renders outgoing Lore email bodies and subjects for new patches and replies.

Important APIs/types/functions: embedded `templatesFS`, `TemplateData`, `renderTemplate`, `RenderBody`, `GenerateSubject`, and `quote`.

Control flow: `RenderBody` prepares template data, formats patch description with fixes/tools/authors/recipients/links/tags, selects `new_patch.txt` or `replies.txt`, and executes it. `GenerateSubject` builds `[PATCH RFC vN] subject` for patches or `Re:` reply subjects. `quote` prefixes every line for email replies.

State and persistence: embeds template text at build time; mutates `res.Patch.Body` to formatted content.

Dependencies and integration: uses dashboard report structs, `pkg/aflow/ai` recipients, email formatting helpers, `net/mail`, and Go text templates.

Risks: invalid recipient address aborts rendering when upstreaming is possible. Mutating poll result body can surprise callers. Empty report result is an error.

Test signals: `templates_test.go` renders fixtures and supports golden update mode.
