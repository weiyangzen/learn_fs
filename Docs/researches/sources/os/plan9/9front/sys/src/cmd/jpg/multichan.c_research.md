# File Research: sources/os/plan9/9front/sys/src/cmd/jpg/multichan.c

This helper converts drawable images to separate color channels when required by writers.

Key behavior:
- Leaves GREY1/2/4/8 and RGB24 images unchanged.
- Converts other `Image` objects to RGB24 by drawing into a new RGB24 image.
- Provides the same operation for `Memimage`.
- Used by writer frontends that need one byte per color component and no alpha/X channel.

Research notes:
- If no conversion is needed, ownership of the original image remains with the caller.
