# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/ti.c

Classifies horizontal/vertical line intersections for table rule drawing.

Key points:
- `interv` determines how a vertical line at column boundary `c` intersects a horizontal rule at row `i`, returning `TOP`, `BOT`, `THRU`, or no intersection.
- Handles double boxes specially at left/right borders.
- `interh` performs the complementary classification for horizontal context around a vertical line, considering full bottom rules and double-box borders.
- `up1` skips replacement rows while looking upward for the previous meaningful row.

Dependencies and interactions:
- Calls `lefdata`, `allh`, `thish`, and `up1`.
- Used by `drawline` and `drawvert` to slightly extend or retract rule endpoints so intersections render correctly.

Research relevance:
- Encodes the geometry needed for visually coherent table borders and internal rules.
