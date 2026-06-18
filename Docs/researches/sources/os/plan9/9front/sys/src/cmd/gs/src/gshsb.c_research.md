# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gshsb.c

## Role

`gshsb.c` implements Ghostscript HSB color setters/getters by converting between HSB and RGB.

This is color conversion infrastructure, not filesystem code.

## Main Interfaces

- `gs_sethsbcolor`
- `gs_currenthsbcolor`

## Core Behavior

`gs_sethsbcolor` clamps hue, saturation, and brightness into `[0, 1]`, converts HSB to RGB, and calls `gs_setrgbcolor`.

`gs_currenthsbcolor` fetches current RGB color with `gs_currentrgbcolor` and converts it to HSB.

Internal conversion uses algorithms attributed to Rogers, “Procedural Elements for Computer Graphics,” and Ghostscript fixed `frac` arithmetic.

## Notable Details

- Gray RGB values map to hue 0, saturation 0, brightness equal to any RGB component.
- HSB hue is multiplied by 6 and dispatched by sector.
- Debug logging can print intermediate HSB-to-RGB conversion state.
