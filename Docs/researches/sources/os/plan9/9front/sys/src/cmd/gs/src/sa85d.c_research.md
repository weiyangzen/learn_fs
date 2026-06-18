# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sa85d.c

Implements the `ASCII85Decode` stream filter. It decodes groups of five ASCII85 digits into four binary bytes, recognizes `z` as a compressed zero group, ignores scanner-classified whitespace, and terminates on `~>`.

The filter is resumable across stream buffer boundaries through `stream_A85D_state.odd` and `word`. It checks for output-buffer capacity, detects ASCII85 overflow, handles odd final groups, and accepts CR/LF between `~` and `>` for Acrobat compatibility despite stricter PostScript language wording.

Dependencies include `strimpl.h`, `sa85d.h`, and `scanchar.h`. It exports `s_A85D_template`.

Risk notes: malformed streams return `ERRC`; finalization with a single dangling digit is invalid. This is stream codec logic, not filesystem code.
