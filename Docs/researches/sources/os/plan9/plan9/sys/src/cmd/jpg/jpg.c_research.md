# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/jpg.c

## Purpose
JPEG viewer/converter front end.

## Behavior
Reads JPEGs through `Breadjpg`, optionally repeatedly for movie-like streams, converts decoded `Rawimage` data to display/output format, and can display, dump compressed rawimage, or write uncompressed Plan 9 image data.

## Options
Supports common conversion flags plus JPEG-specific `-J` decode-only, `-r` output RGB rather than YCbCr, `-y` keep YCbCr for debugging, `-f` merge two fields per image, and `-F` movie mode with field merge.

## Field Merge
`vidmerge()` interleaves scanlines from paired decoded images, doubling the output height and freeing source channel buffers.

## Dependencies
Uses `Breadjpg`, `torgbv`, `totruecolor`, `writerawimage`, Bio, libdraw, and event handling.
