# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/stylelist.c

This file stores paragraph style runs and normalizes list/indentation data for rendering.

Key behavior:
- Maintains a linked list of style records keyed by file offset and sequence number.
- Converts Word list bullet/private-use characters into output-specific text or UTF-8.
- Clamps excessive before/after paragraph spacing and corrects negative/invalid indents.
- Provides ordered iteration, text-only style iteration, and `usGetIstd()` lookup by file offset.
- Determines whether a paragraph style implies list membership.

Important details:
- Consecutive records at the same file offset collapse to the last style.
- A midpoint pointer and sequence-order flag optimize `usGetIstd()` scans.
- Heading styles are explicitly excluded from list detection.

Filesystem relevance:
- Indirect: ties parsed file offsets to layout/list rendering state.
