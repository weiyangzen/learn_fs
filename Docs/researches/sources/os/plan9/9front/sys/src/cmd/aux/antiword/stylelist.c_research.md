# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/stylelist.c

Stores parsed style transitions and normalizes list/indent behavior for rendering.

Key responsibilities:
- Maintains a linked list of `style_block_type` records keyed by file offset/sequence number.
- Converts Word list bullet/private-use characters into UTF-8 or ASCII-compatible output markers.
- Normalizes invalid or excessive indentation and gives headings a minimum vertical gap.
- Tracks whether style records are in sequence and keeps a midpoint pointer for faster lookup.
- Provides sequential style iteration and text-only style iteration that skips header/footer, macro, and annotation lists.
- Maps file offsets back to current `istd` for character font inheritance.
- Determines whether a paragraph style implies list membership.

Dependencies:
- List constants, encoding/conversion options, sequence-number mapping, stylesheet defaults, output bullet helpers.

Notable risks:
- List character conversion contains many heuristic mappings for Symbol/private-use bullets.
- `usGetIstd()` relies on sequence-number ordering for its fast path but has a full scan fallback.
