# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zhsb.c

## Purpose
Implements HSB color operators.

## Key Functions
- `zcurrenthsbcolor()` pushes current hue, saturation, and brightness.
- `zsethsbcolor()` validates three numeric parameters and sets the graphics-state color.

## Important Behavior
- `sethsbcolor` clears the interpreter cached color-space array after setting an HSB color.
- Operators are registered as `currenthsbcolor` and `sethsbcolor`.

## Research Notes
Small color-space operator wrapper around `gshsb.h`.
