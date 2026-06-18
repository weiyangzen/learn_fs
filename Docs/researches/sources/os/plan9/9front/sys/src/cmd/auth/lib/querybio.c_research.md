# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/querybio.c

Interactive account biography editor.

Key responsibilities:
- Loads existing bio data with `rdbio`.
- Prompts for post id, full name, department, primary email, sponsor email, and additional email addresses.
- Supports retaining defaults, clearing optional fields with a space, and marking whether data changed.
- Returns whether any field changed.

Dependencies:
- Uses `Acctbio`, `Nemail`, `readcons`, and `rdbio`.
