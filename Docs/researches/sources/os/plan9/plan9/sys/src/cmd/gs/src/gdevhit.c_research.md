# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevhit.c

Minimal hit-detection device for insideness testing.

Key behavior:
- Exports `gs_hit_detected = gs_error_hit_detected`.
- Defines `gs_hit_device`.
- `hit_fill_rectangle` returns `gs_error_hit_detected` for any positive-area fill.

Risks / notes:
- Intentionally non-rendering; the “hit” is signaled through error control flow.
