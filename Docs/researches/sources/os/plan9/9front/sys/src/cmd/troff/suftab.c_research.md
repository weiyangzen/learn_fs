# File Research: sources/os/plan9/9front/sys/src/cmd/troff/suftab.c

This file is a static suffix-pattern table for troff hyphenation. It defines `Uchar` arrays named by final letter (`sufa`, `sufc`, `sufd`, etc.) and exports `Uchar *suftab[]`, indexed by alphabet position, to locate applicable suffix rules.

Each rule is byte-coded: the first byte encodes length plus flags, and subsequent bytes encode suffix characters, with `0200+ch` marking hyphenation break positions. The comments show the intended word-part pattern, such as `-TION`, `-ABLE`, `-ING`, or `AL-I-ZA-TION`.

There is no executable logic here. It is data consumed by troff’s older hyphenation algorithm. Maintenance risk is mainly semantic opacity: the octal flags and high-bit markers require knowledge of the hyphenation engine to edit safely.
