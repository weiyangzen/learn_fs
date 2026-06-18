# sources/test-tools/syzkaller/dashboard/config/linux/main.yml Research

## Purpose
This is the central Linux dashboard instance matrix. It maps named syzbot managers to tag lists and maps config bit files to predicates controlling when those bits are included.

## Important data and APIs
- `instances` defines concrete dashboard manager names such as upstream KASAN/KMSAN/KCSAN, architecture variants, stable branches, Android, and ChromeOS lanes.
- `includes` lists fragment files from `bits/` in deterministic order. Later includes may override earlier config choices.
- The file contains about 105 instance entries and 64 include entries in the local YAML list format.

## Control flow
The dashboard config tooling reads an instance's tag list, walks `includes` top to bottom, and includes each fragment whose predicate list matches. Tags encode kernel tree, architecture, timeout model, compiler, LSM, sanitizer, reporting policy, and reduced/baseline/onlynet/onlyusb variants.

## State and persistence
No runtime state is stored here, but this file persistently defines all generated Linux dashboard configs. Updating an instance tag or include predicate changes future generated kernel configs and can alter syzbot coverage or public reporting.

## Dependencies and integration points
It depends on every referenced `bits/*.yml` file, the dashboard config parser, Linux Kconfig, syz-ci manager naming, and kernel tree selectors. Comments document known upstream breakage and coverage tradeoffs such as arm lockdep, hamradio removal, and full arm64 configs for `syz-check`.

## Risks
The main risks are include-order regressions, tag typos that drop critical fragments, unintentional public reporting from unmaintained surfaces, and stale stable/next tags. Instance names are integration contracts with dashboard and syz-ci deployments.

## Test signals
Validation should parse all instances, assert all referenced fragment files exist, generate configs for every manager, and boot-smoke representative managers. This research pass read the file directly and did not run dashboard config generation.
