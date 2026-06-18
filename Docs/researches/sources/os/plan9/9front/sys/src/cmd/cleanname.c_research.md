# File Research: sources/os/plan9/9front/sys/src/cmd/cleanname.c

Small command-line wrapper around Plan 9 `cleanname`. It normalizes pathnames and prints the cleaned results.

Supports `-d pwd`; relative input names are prefixed with that directory before cleaning, while absolute names or no `-d` are cleaned in place.

Allocates a temporary combined path for `-d` relative cases and exits on allocation failure.

Usage: `cleanname [-d pwd] name...`.
