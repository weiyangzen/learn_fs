# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/flchk.c

Command-line wrapper around `fsCheck`.

It parses cache size, Venti host, local-only checking, and directory printing flags, connects to Venti when needed, opens the fossil image read-only, installs formatters, and runs the checker. Repair hooks print commented console-style repair commands such as `# clre`, `# clrp`, `# clri`, and `# bclose` rather than applying changes directly.

This makes `flchk` a diagnostic and repair-script-generation tool.
