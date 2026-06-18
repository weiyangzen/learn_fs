# sources/test-tools/strace/maint/gen-release-notes.sh

Purpose: emits release notes as HTML-preformatted text.

Important APIs/types/functions: prints `<pre>`, invokes adjacent `gen-tag-message.sh`, prints `</pre>`.

Control flow: a simple three-step wrapper with strict shell mode.

State and persistence behavior: no persistent state; stdout is the artifact.

Dependencies and integration points: integrates with release channels that expect preformatted HTML rather than Markdown.

Risks: no escaping is performed, so unexpected HTML-significant characters from NEWS or contributor names could affect rendering. It depends wholly on `gen-tag-message.sh` correctness.

Test signals: generated text should contain the current release NEWS excerpt and contributor block enclosed in a single preformatted element.
