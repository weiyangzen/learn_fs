# File Research: sources/os/plan9/plan9/sys/src/cmd/scat/image.c

Builds a cropped grayscale DSS `Picture` for a requested sky location and angular size.

Key flow:
- Initializes gamma defaults and derived gamma fields.
- Loads the plate list if needed and chooses the nearest plate by angular distance.
- Reads the plate header and converts requested RA/Dec to plate x/y coordinates.
- Computes crop bounds, clamps to the 14000x14000 plate extent, and allocates output bytes.
- Iterates 500x500 subplates, mounts/opens DSS tile files, decodes with `dssread`, and copies gamma-corrected pixels into the output crop.

Behavior notes:
- Region subplate names use radix-28 characters from `rad28`.
- If no width/height is supplied, a default 500x500 plate-aligned tile is chosen.
- Returns a `Picture` with crop bounds, plate name, and raw 8-bit data suitable for `displaypic`.
