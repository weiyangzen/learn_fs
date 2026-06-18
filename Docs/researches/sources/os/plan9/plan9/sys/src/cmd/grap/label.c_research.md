# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/label.c

This file emits graph labels and text sizing/positioning. It tracks point size, label width override, and accumulated label movement offsets.

`label` computes text height/width, emits a `Label` invisible box from a string list, positions it relative to the selected frame side, applies accumulated movement, and frees attributes.

`sizeit` wraps strings in troff size escapes based on per-string size operations or global `pointsize`.
