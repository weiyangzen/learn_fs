# File Research: sources/os/plan9/9front/sys/src/cmd/grep/comp.c

Incremental DFA compiler and UTF class expander for Plan 9 `grep`. `increment` computes the follow set for a state and input byte, interns equivalent states in a binary tree, and records transitions lazily in `State.next`.

`fol1` advances regex fragments for bytes, anchors, alternations, classes, and case nodes. `re2class` parses rune ranges, merges overlaps, handles negation, and converts Unicode rune ranges into byte-level regex fragments using UTF-8 range splitting via `rclass`.
