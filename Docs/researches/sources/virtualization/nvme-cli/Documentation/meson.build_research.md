# File Research: sources/virtualization/nvme-cli/Documentation/meson.build

- Purpose: Meson documentation build/install definition.
- Main content: declares the large `adoc_sources` list of nvme command manpage/documentation stems, including core NVMe, fabrics, ZNS, SED, and vendor plugin commands.
- Includes: copies shared include fragments such as `cmd-plugins.txt`, `cmds-main.txt`, `global-options.txt`, and `fabrics-options.txt`.
- Build behavior: when docs are enabled and `asciidoc`/`xmlto` are available, generates DocBook, man pages, and XHTML via `custom_target`.
- Fallback behavior: if docs build tools are absent, installs precompiled `.1` and `.html` files.
