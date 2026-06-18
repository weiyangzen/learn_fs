# File Research: sources/os/bsd/openbsd-src/sbin/wsconsctl/mousecfg.c

Implements reusable wsmouse parameter handling for mouse and touchpad configuration.

Key behavior:
- Defines grouped `struct wsmouse_parameters` presets for tapping, multitouch buttons, scaling, edges, side swapping, disable, reverse scrolling, and raw param access.
- `mousecfg_init()` detects touchpad devices, reads calibration resolution, builds a parameter buffer, and reads base/touchpad parameter ranges with `WSMOUSEIO_GETPARAMS`.
- `index_of()` maps enum parameter keys into the local buffer across supported ranges.
- `mousecfg_get_field()` copies values from the cached buffer into a field.
- `mousecfg_put_field()` writes changed values with `WSMOUSEIO_SETPARAMS`, then immediately reads normalized values back.
- Input helpers parse tapping triples, edge percentages, scaling factors, and raw `key:value` parameter lists.
- Print helpers serialize fields in stable human-readable forms.

Filesystem/OS relevance:
- Good example of kernel parameter discovery, caching, normalization, and userland validation around ioctl arrays.
