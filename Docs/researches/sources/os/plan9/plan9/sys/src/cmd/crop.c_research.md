# File Research: sources/os/plan9/plan9/sys/src/cmd/crop.c

Image crop/translate utility built on Plan 9 `memdraw`.

It reads a `Memimage` from stdin or a file, optionally computes the non-background bounding rectangle for a specified RGB crop color, applies uniform inset, x/y inset, or absolute rectangle selection, fills the destination with a background color or opaque black, draws the clipped source into the new image, applies an output coordinate translation, and writes the image.

The crop-color scan converts non-RGBA32 images to RGBA32 for simple pixel comparison.
