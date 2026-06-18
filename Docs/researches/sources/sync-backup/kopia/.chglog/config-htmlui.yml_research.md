# sources/sync-backup/kopia/.chglog/config-htmlui.yml

Purpose: changelog generator configuration for the Kopia HTML UI repository.

Important APIs/types/functions: GitHub style, `CHANGELOG_HTMLUI.tpl.md`, repository URL `kopia/htmlui`, commit scope filters, group title maps/order, header regex, and breaking-change note keywords.

Control flow: static config for changelog tooling; commits are filtered/grouped by parsed conventional-commit scope.

State and persistence: no runtime state; controls generated changelog output.

Dependencies and integration points: scope list and title maps must align with PR title workflow comments.

Risks: scopes not listed are excluded from changelog output; divergence from PR title regex can drop valid changes.

Test signals: no direct tests; CI title workflow is the consistency signal.
