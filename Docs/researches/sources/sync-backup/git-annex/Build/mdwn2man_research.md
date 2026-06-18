# sources/sync-backup/git-annex/Build/mdwn2man

Purpose: quick Perl converter from ikiwiki-style markdown snippets to manpage roff.

Important APIs/types/functions: reads stdin, prints `.TH`, rewrites wiki links, inline backticks, headings, paragraphs, list items, hyphens, escaped dots, NAME section command names, and quote escapes.

Control flow/state: line-oriented filter with state flags for list context, paragraph skipping, and NAME section handling. It intentionally uses simple regex transformations rather than a full Markdown parser.

Dependencies/integration: part of git-annex documentation/manpage build tooling.

Risks/test signals: labeled as a hack; complex markdown can render incorrectly. Manpage generation and `lexgrog`-style NAME validation are the likely regression signals.

Source research group: `subset-b-009122`.
