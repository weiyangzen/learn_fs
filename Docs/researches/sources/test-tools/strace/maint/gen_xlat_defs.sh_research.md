# sources/test-tools/strace/maint/gen_xlat_defs.sh

Purpose: regenerates xlat `.in` definitions from Linux UAPI headers while preserving comments/directives and representing architecture-specific value differences with preprocessor guards.

Important APIs/types/functions: Bash option parser for `-f`, `-p`, `-d`, `-c`, and `-a`; sed/grep extraction of common and arch-specific `#define`s; embedded awk `mystrtonum` for octal/hex/decimal conversion; emitted `#if/#elif/#else/#endif` blocks.

Control flow: validate all required options, print a generated-by header, read existing xlat content from stdin, pass through comments/empty directives, and for each constant search common headers for a default value and arch headers for overrides. The awk stage groups differing values by architecture macros and emits guarded xlat entries.

State and persistence behavior: reads stdin and kernel source tree; writes stdout only. It logs warnings for missing or resolved definitions to stderr.

Dependencies and integration points: feeds xlat maintenance for constants whose numeric values vary by architecture. Its generated header is parsed by `list-xlat-linux-headers.sh` and `update-xlat` workflows.

Risks: shell globbing over kernel header patterns and regex extraction can be fragile. The script is Bash-specific despite a `/bin/bash` shebang. Architecture macro normalization is hard-coded for arm64/aarch64 and x86.

Test signals: regenerated xlat files should preserve existing comments, include correct default and arch-guarded values, and compile through xlat generation.
