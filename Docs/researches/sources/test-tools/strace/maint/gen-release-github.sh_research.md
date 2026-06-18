# sources/test-tools/strace/maint/gen-release-github.sh

Purpose: formats a release announcement body for GitHub releases.

Important APIs/types/functions: invokes `gen-tag-message.sh`, escapes literal asterisks with sed, and appends a Downloads warning telling readers to ignore GitHub-generated source links.

Control flow: stream tag message through sed, then append a fixed Markdown downloads section.

State and persistence behavior: no persistent state; output is stdout.

Dependencies and integration points: used in release publication flow after `gen-tag-message.sh`. Integrates with GitHub release notes UI conventions.

Risks: Markdown escaping is broad and can alter intended emphasis. The generated download section contains placeholder text rather than artifact-specific checksums or URLs.

Test signals: rendered GitHub release text should preserve NEWS formatting, contributor bullets, and the downloads warning without broken Markdown.
