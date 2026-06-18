# File Research: sources/os/plan9/9front/sys/src/cmd/astro/nutate.c

Computes nutation, obliquity, and Greenwich sidereal time.

Important behavior:
- Derives lunar and solar fundamental arguments from `eday`/`capt`.
- Uses `nutfp`/`nutcp` tables through `sinadd`/`cosadd`.
- Sets `phi`, `eps`, `dphi`, `deps`, `obliq`, `tobliq`, and `gst`.
- Applies nutation correction to sidereal time.

This state feeds coordinate transforms in `helio`, `moon`, and `geo`.
