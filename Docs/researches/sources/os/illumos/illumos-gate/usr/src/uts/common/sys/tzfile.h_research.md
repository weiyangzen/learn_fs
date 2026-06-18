# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tzfile.h

## Purpose
Time zone file format and calendrical constant definitions.

## Main Interfaces
- Defines zoneinfo paths and defaults: `TZDIR`, `TZDEFAULT`, and `TZDEFRULES`.
- Defines `struct tzhead`, the on-disk time zone file header.
- Defines maximum counts for transitions, types, abbreviations, and leap corrections.
- Defines calendar constants for seconds/minutes/hours/days/months, weekday and month indexes, epoch year/weekday, and `isleap`.
- Provides alternate uppercase constant names such as `SECS_PER_MIN`, `MINS_PER_HOUR`, and `DAYS_PER_LYEAR`.

## Dependencies And Relationships
Used by timezone parsing and libc time conversion code that reads zoneinfo files.

## Research Notes
The file reflects the historical tzfile layout and should be kept aligned with timezone data reader expectations.
