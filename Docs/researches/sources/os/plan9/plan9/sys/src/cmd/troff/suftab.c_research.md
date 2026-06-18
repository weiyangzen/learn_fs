# File Research: sources/os/plan9/plan9/sys/src/cmd/troff/suftab.c

Read fully: 612 lines, 19337 bytes. SHA-256 prefix: `f5f174e8a1b058ce`.

This is a static suffix-pattern table for troff hyphenation. It defines `Uchar` arrays `sufa`, `sufc`, `sufd`, `sufe`, `suff`, `sufg`, `sufh`, `sufi`, `sufk`, `sufl`, `sufm`, `sufn`, `sufo`, `sufp`, `sufr`, `sufs`, `suft`, and `sufy`, then indexes them through `suftab[]` by final letter.

The data encodes suffixes and preferred hyphenation points with high-bit-marked characters and flag bits in the leading length byte. Comments document examples such as `-TION`, `-ABLE`, `-ING`, `-NESS`, `-BILITY`, and many other English endings.

Integration: consumed by troff’s hyphenation algorithm, alongside exception lists and TeX-style hyphenation support. There is no executable logic in this file.

Risk notes: this is compact, hand-maintained table data. Any edit needs to preserve the encoded byte convention, zero terminators, and `suftab[]` letter alignment.
