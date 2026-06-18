# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ztrans.c

## Purpose
Implements PostScript/PDF transparency-related interpreter operators.

## Key Elements
Provides blend mode, opacity alpha, shape alpha, and text knockout getters/setters. Implements transparency group/mask begin/end/discard/init operators, ImageType 3x soft-mask image setup, and pdf14 transparency device filter push/pop.

## Behavior/Risks
Dictionary parsing validates required transparency keys such as `Subtype`, optional backgrounds, transfer functions, mask dictionaries, and interleave constraints. Transparency masks may use a Ghostscript function as a one-input/one-output transfer function. `image3x` rewires mask data sources before image data sources for interleaved soft masks. Discard operators range-check the current transparency state before dropping a layer.

## Dependencies
Uses graphics state transparency APIs from `gstrans.h`, color space APIs, image parameter parsing, function evaluation, dictionary parameter helpers, and pdf14 device support.
