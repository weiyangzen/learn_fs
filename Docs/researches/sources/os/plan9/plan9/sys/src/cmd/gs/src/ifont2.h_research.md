# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ifont2.h

Declares Type 2-specific font parameter parsing.

Key points:
- Defines Type 2 default `lenIV` as `-1`.
- Declares `type2_font_params`, which extracts Type 2 parameters beyond common Type 1/Type 2 CharString parameters.
- Depends on `charstring_font_refs_t` and `gs_type1_data`.

Research relevance:
- Small specialization point for Type 2/CFF-style font handling.
