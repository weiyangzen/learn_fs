# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/rlist.c

## Role

`rlist.c` maintains a compact list of dirty rectangles for VNC framebuffer updates.

## Main Behavior

- `growrlist()` expands the rectangle array and enforces a global `tot` cap of 10000 allocated rectangle slots.
- `addtorlist()` adds a rectangle to an `Rlist` while trying to merge, trim, or split against existing rectangles.
- Handles covered rectangles, covering rectangles, aligned merges, edge subtraction, corner overlap splitting, and band splitting.
- Maintains `bbox` as the overall bounding box.
- `freerlist()` releases storage and updates the global allocation counter.

## Notable Limitations And Risk Areas

- Complex overlaps outside the handled cases call `abort()`.
- The rectangle budget is global, not per-client.
- `bbox` is updated before the merge/split process and may remain a conservative bounding box.
- The debug `main()` is only compiled under `REGION_DEBUG`.
