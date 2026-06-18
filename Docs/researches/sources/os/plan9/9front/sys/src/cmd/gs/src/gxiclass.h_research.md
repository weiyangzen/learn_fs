# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxiclass.h

## Role

`gxiclass.h` defines the image rendering class interfaces used to choose and call Ghostscript image renderers.

This is image rendering infrastructure, not filesystem code.

## Main Definitions

- Forward declares `gx_image_enum` and `gx_device`.
- `irender_proc(proc)`: macro signature for scan-line render procedures.
- `irender_proc_t`: function pointer type for render procedures.
- `iclass_proc(proc)`: macro signature for image-class selector procedures.
- `gx_image_class_t`: function pointer type for class selectors.

## Interface Semantics

- Render procedures receive expanded complete rows and return a negative error code or number of rows processed.
- `height == 0` is a flush/end-of-input signal for renderers.
- The `w` argument is the number of samples, not pixels and not bytes; this matters for multi-component and 12-bit-expanded images.
- Class selector procedures are called in alphabetical/priority order and may update the image enumerator before returning a renderer.

## Notable Risks

- The "w is samples" contract is easy to violate because many callers naturally think in pixels or bytes.
- The class selection priority is implicit in function names, so renaming can affect renderer choice.
