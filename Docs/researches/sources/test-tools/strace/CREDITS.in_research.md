<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/CREDITS.in -->
# sources/test-tools/strace/CREDITS.in

Purpose: template for generating strace's human-readable `CREDITS` file.

Important content: static introduction names the primary authors and explains contributor inclusion. A marker block beginning with `##<`/`##>` separates comments for the generator from manually listed contributors. Manual entries are name/address pairs for contributors not expected to appear as Git authors.

Control flow: no executable code, but `Makefile.am` processes it in maintainer mode: it emits the pre-marker text, extracts post-marker entries, normalizes spacing to tabs, passes them through `maint/gen-contributors-list.sh`, then indents output.

State and persistence: source template persists in VCS; generated `CREDITS` is build artifact or distribution content.

Dependencies and integration: coupled to `.mailmap`, Git history, and `maint/gen-contributors-list.sh`.

Risks: stale or malformed manual entries can affect generated credits. Non-ASCII names require encoding-preserving tooling. The comment marker protocol is implicit and easy to break. Test signals: `make CREDITS` in maintainer mode should regenerate a stable sorted contributor list.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/CREDITS.in -->
