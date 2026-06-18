# File Research: sources/os/plan9/9front/sys/src/cmd/auth/lib/getexpiration.c

Interactive account expiration-date helper.

Key responsibilities:
- Reads an existing `<db>/<user>/expire` value when present.
- Displays defaults as `YYYYMMDD` or `never`.
- Prompts for a new expiration date.
- Accepts empty input as unchanged sentinel `-1`, `never` as `0`, or a date within now and two years from now.
- Converts accepted dates to seconds.

Dependencies:
- Uses Plan 9 `Tm`, `tm2sec`, `localtime`, and console prompting.
