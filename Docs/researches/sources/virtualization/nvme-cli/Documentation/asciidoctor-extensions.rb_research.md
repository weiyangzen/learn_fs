# File Research: sources/virtualization/nvme-cli/Documentation/asciidoctor-extensions.rb

- Purpose: Asciidoctor Ruby extension for `linknvme`.
- Key behavior: registers an inline macro processor that renders links differently for HTML, manpage, and DocBook backends.
- HTML output: emits `<a href="target.html">target(section)</a>`.
- DocBook output: emits `citerefentry/refentrytitle/manvolnum`.
