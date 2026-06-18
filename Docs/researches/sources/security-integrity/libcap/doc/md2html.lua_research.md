## sources/security-integrity/libcap/doc/md2html.lua

Purpose: Pandoc Lua filter that rewrites markdown links ending in `.md` to `.html` during generated manpage HTML rendering.

Important APIs/functions: `Link(el)` callback and `string.gsub`.

Control flow: every Pandoc link element is visited; its target string has `.md` replaced by `.html`; the modified element is returned.

State/persistence: no persistent state; transformation is in-memory during Pandoc processing.

Dependencies/integration: Pandoc Lua filter API. Used by the comment in `mkmd.sh` for markdown-to-HTML conversion.

Risks: global replacement can rewrite `.md` anywhere in a URL, not only as a suffix; external links containing `.md` may be altered unintentionally.

Test signals: run Pandoc with the filter against generated markdown containing local and external links and check final hrefs.
