# File Research: sources/os/bsd/netbsd-src/lib/libc/time/checktab.awk

## Purpose
Validates tzdb country and zone table consistency.

## Key Elements
Reads `iso3166.tab` and a selected zone table, verifies column counts, country-code format/order/duplicates, coordinate format, country use, comment necessity, zone coverage, and rule usage. It includes temporary/special accepted zones and can emit warnings for countries without zones.

## Dependencies
Uses awk with tab-separated parsing for tables, then space-separated parsing for zone data files.

## Behavior/Risks
Reports errors to stderr and exits nonzero on inconsistencies. Special-case zone exemptions are embedded, so policy updates require script maintenance.
