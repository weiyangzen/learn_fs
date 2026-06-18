# sources/test-tools/strace/maint/gen-release-gitlab.sh

Purpose: formats release text for GitLab, including upload links for local `strace-*.tar.xz*` artifacts.

Important APIs/types/functions: shell glob expansion, `set +f`/`set -f`, fixed Markdown output, and `gen-tag-message.sh` piped through sed asterisk escaping.

Control flow: print a Downloads header, iterate matching tarball files and emit placeholder `/uploads/...` links, print the GitLab source-link warning, then append the escaped tag message.

State and persistence behavior: reads current directory artifact names and writes stdout only.

Dependencies and integration points: used after distribution artifact generation, likely with manual replacement of upload placeholders in GitLab release drafting.

Risks: if no glob matches, POSIX shells can leave the literal pattern as a file candidate. Upload path placeholder `"..."` requires human or CI replacement. Markdown escaping can affect intended formatting.

Test signals: in a release directory, output should list each tarball/signature and render cleanly in GitLab Markdown.
