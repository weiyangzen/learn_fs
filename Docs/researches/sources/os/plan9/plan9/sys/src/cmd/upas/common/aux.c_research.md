# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/aux.c

- Role: Shared string/path/address utility functions for upas tools.
- Key functions: `abspath`, `basename`, `append_match`, `shellchars`, `escapespecial`, `unescapespecial`, `returnable`.
- Behavior: Encodes shell-special characters as `%%HH`, decodes those escapes, and flags CR/LF as illegal shell characters.
- Integration: Declared in `common.h`.
- Risks/notes: Only escapes a fixed special-character set; callers must not treat it as a complete shell quoting system.
