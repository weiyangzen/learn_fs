# File Research: sources/os/bsd/freebsd-src/sbin/rcorder/rcorder-visualize.sh

Small shell helper to emit Graphviz dot for rc script dependency comments.

Key elements:
- Defaults input files to `/etc/rc.d/*` or accepts file arguments.
- Emits `digraph { ... }`.
- For each file, awk extracts one `# PROVIDE:` token, all `# REQUIRE:` tokens, and all `# BEFORE:` tokens.
- Prints provider nodes, provider-to-requirement edges, and before-to-provider edges.

Dependencies:
- POSIX shell, awk, and Graphviz for optional rendering.

Research notes:
- This is a lightweight visualizer, not a full `rcorder` equivalent; it does not implement keyword filtering, multiline parsing, duplicate providers, fake provisions, or cycle handling.
