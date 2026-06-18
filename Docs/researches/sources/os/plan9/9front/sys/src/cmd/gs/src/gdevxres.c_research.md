# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevxres.c

Static Xt resource definitions for the Ghostscript X11 device.

Key contents:
- `gdev_x_resources[]` maps Xt resource names/classes to fields inside `gx_device_X`.
- Resources cover background/foreground/border, geometry, logging, max gray/RGB ramp sizes, palette mode, font map strings, X-font behavior, backing pixmap, XPutImage/XSetTile workarounds, and x/y resolution.
- Large default PostScript-to-X11 font mappings are embedded for standard fonts, Symbol, and ZapfDingbats.
- `gdev_x_resource_count` exports table length.
- `gdev_x_fallback_resources` provides default white background and black foreground.

Notable implementation details:
- The table is isolated because Xt declares resource strings as mutable `char *`, creating noisy cast-qual warnings.
- Comments note Xt may actually write into these structures, so they are not `const`.

Filesystem relevance:
- None.
