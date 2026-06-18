# File Research: sources/os/plan9/9front/sys/src/cmd/aux/gps/util.c

Role: Shared GPS position parsing, formatting, and RTC update helpers.

Position formatting:
- `placeconv` implements `%L` by formatting latitude and longitude as degrees/minutes/seconds with N/S/E/W suffixes.

Parsing:
- `strtolatlon` accepts signed decimal or colon-separated degrees/minutes/seconds and optional hemisphere suffix.
- It fills the first unset coordinate in a `Place`, rejects duplicate coordinate assignment, and supports implicit latitude then longitude ordering.
- `strtopos` parses two coordinates and returns `nowhere` on failure.

RTC:
- `rtcset` opens `#r/rtc`, reads current RTC seconds, validates it, and writes GPS time when drift exceeds the function's threshold logic.

Notes:
- Uses `Undef` as a coordinate sentinel, stored in doubles via integer macro value.
