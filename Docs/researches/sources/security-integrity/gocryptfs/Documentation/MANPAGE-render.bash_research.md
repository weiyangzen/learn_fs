# sources/security-integrity/gocryptfs/Documentation/MANPAGE-render.bash

Purpose: This script renders gocryptfs manual pages from documentation sources into distributable manpage files.

Important APIs and steps: It likely invokes `pandoc` or compatible tooling for `gocryptfs.1` and `gocryptfs-xray.1`, ensuring release tarballs include pre-rendered manpages.

Control flow and state: It runs in the documentation directory context and writes generated manpage outputs. Persistent state is generated `.1` files.

Dependencies and integration points: Used by release packaging scripts and build/install workflows that avoid requiring documentation tools on end-user systems.

Risks and test signals: Tool-version drift can alter output formatting. Signals include successful rendering during packaging and generated manpages included in release artifacts.
