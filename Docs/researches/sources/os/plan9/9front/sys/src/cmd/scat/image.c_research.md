# File Research: sources/os/plan9/9front/sys/src/cmd/scat/image.c

Purpose: Builds an 8-bit grayscale DSS picture for a sky coordinate and requested angular size.

Flow:
- Initializes gamma defaults and derived gamma scaling.
- Loads plate inventory if needed.
- Chooses the closest DSS plate by angular distance.
- Converts requested RA/Dec to plate pixel coordinates through `getheader` and `xypos`.
- Computes target plate rectangle, clamps it to `0..14000`.
- Reads all 500x500 subplate tiles intersecting the rectangle through `dssmount` and `dssread`.
- Gamma maps pixels with `dogamma` and assembles a `Picture`.

Integration: Uses `plate[]`, `getplates`, `getheader`, `xypos`, `dssmount`, `dssread`, and global `gam`.

Risks:
- Subplate index uses `rad28`; out-of-range subplates abort the image request.
- The pixel indexing uses DSS tile layout assumptions with `ny` as fast-varying dimension.
- Returns `nil` on allocation/read failures after printing diagnostics.
