# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/read.c

Parses the blkid cache file into in-memory cache/device/tag objects.

Cache format:
- One device per line:
  - `<device DEVNO="..." TIME="..." TYPE="..." ...>/dev/name</device>`
- Required tags documented:
  - `ID`, `TIME`, `TYPE`
- Optional tags documented:
  - `LABEL`, `UUID`

Key functions:
- Text helpers:
  - `skip_over_blank`
  - `skip_over_word`
  - `strip_line`
- Parsing helpers:
  - `parse_start`
  - `parse_end`
  - `parse_dev`
  - `parse_token`
  - `parse_tag`
- `blkid_parse_line(cache, dev_p, cp)`
  - Parses one cache line.
  - Creates/fetches the device object.
  - Applies tags and direct fields.
  - Drops device if no `TYPE`.
- `blkid_read_cache(cache)`
  - Opens cache file.
  - Skips reread if mtime unchanged or cache is dirty.
  - Handles backslash-continued lines.
  - Parses each line and updates `bic_ftime`.
  - Clears `BLKID_BIC_FL_CHANGED` after successful initial read.

Direct field parsing:
- `DEVNO` into `bid_devno`
- `PRI` into `bid_pri`
- `TIME` into `bid_time`
- Other tags via `blkid_set_tag`

Notable details:
- This is XML-like, not a general XML parser.
- Comments are skipped only when line starts with `#` after leading whitespace.
- Unknown XML-like lines are skipped.
