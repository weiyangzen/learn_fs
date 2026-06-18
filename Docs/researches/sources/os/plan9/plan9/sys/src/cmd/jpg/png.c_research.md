# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/png.c

## Purpose
PNG viewer/converter front end.

## Behavior
Reads PNG via `Breadpng`, converts indexed/truecolor/alpha outputs to the requested display or file channel, optionally displays over a black backing image for alpha composition, and writes Plan 9 raw or compressed rawimage output.

## Options
Supports `-D` decoder debug plus common image flags `-39cdekrtv`.

## Format Handling
Unlike other front ends, it preserves already packed PNG output descriptors such as `CY`, `CYA16`, `CRGB24`, and `CRGBA32` when writing truecolor output.

## Dependencies
Uses `Breadpng`, `torgbv`, `writerawimage`, Bio, libdraw, and event handling.
