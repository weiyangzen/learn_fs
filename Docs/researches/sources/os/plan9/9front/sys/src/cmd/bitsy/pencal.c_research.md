# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/pencal.c

This is a pen/touchscreen calibration utility.

Major responsibilities:
- Reads raw mouse/pen events from `/dev/mouse` or `#m/mouse`.
- Reads/writes calibration data through `#m/mousectl`.
- Displays calibration crosses at four corners and a center verification point.
- Computes linear scale/translation values for x and y.

Notable implementation details:
- Attempts to resize its window to nearly the full display through `/dev/wctl`.
- Reads existing calibration from a 48-byte `mousectl` message.
- Averages samples while button bits are down, ending a point when released.
- Retries calibration up to three times if center verification differs by more than four pixels.

Risks and caveats:
- Assumes fixed-format 48-byte mouse and mousectl messages.
- `scr2pen` uses `(p.y + cal.transy)` where the inverse would usually subtract; this may reflect device convention or a historical quirk.
