# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libmemlayer/unload.c

Layer-aware wrapper for unloading image bytes.

Key function:
- `memunload`: unloads from direct images, clear layers, save backing, or a temporary composited image.

Important behavior:
- Cannot unload refresh-backed obscured layers because there is no reliable saved pixel data.
- Uses `memlhide` before reading from save backing to make sure backing store contains current screen contents.
- Falls back to drawing the layer into a temporary image when unaligned or otherwise indirect.
