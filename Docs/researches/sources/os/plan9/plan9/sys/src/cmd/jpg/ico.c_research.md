# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/ico.c

## Purpose
Interactive Microsoft ICO file viewer/extractor.

## Main Behavior
Parses ICO headers and icon directory entries, loads supported icon images, displays them in a Plan 9 window, and lets button-3 menu actions write the selected image or mask as Plan 9 image files.

## Format Handling
Supports ICO type 1 with 1, 2, 4, and 8 bit indexed BMP-like payloads. It reads little-endian fields, translates BMP color maps to Plan 9 colormap indices, decodes XOR image bits, decodes/inverts AND mask bits, and composes an image over a white background.

## UI
Displays each decoded icon with borders, updates status text on hover, and uses a sight cursor for selecting icons to save.

## Limits
Does not support true-color ICO entries or multiple planes.
