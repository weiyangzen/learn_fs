# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemdraw/drawtest.c

Stochastic test program for `memimagedraw`.

Key behavior:
- Allocates destination, source, mask, and temporary images with configurable channel descriptors.
- Randomizes image contents, including alpha-respecting random pixels.
- Verifies one-pixel, line, rectangle, replicated-source, replicated-mask, and combined replicated cases.
- Compares bulk `memimagedraw` output against repeated one-pixel reference drawing.
- Includes helpers for dumping images, reading/writing pixels in arbitrary channel formats, mask extraction, greyscale conversion, and replication simulation.

Important scope:
- Tests compositing correctness extensively for disjoint source/destination/mask images.
- Explicitly notes it does not test overlapping image behavior.
