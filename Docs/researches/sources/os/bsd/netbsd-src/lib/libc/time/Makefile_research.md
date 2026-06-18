# File Research: sources/os/bsd/netbsd-src/lib/libc/time/Makefile

## Purpose
Upstream tzdb Makefile for building, validating, installing, packaging, and signing timezone code and data.

## Key Elements
Defines package/version/install paths, data formats (`vanguard`, `main`, `rearguard`), leap-second modes, data sets, source lists, man pages, checks, generated files, `zic`, `zdump`, `tzselect`, `libtz.a`, `date`, `tzdata.zi`, `leapseconds`, `version`, `tzdir.h`, `version.h`, zone installs, reproducible timestamps, tarballs, signatures, and typecheck targets.

## Dependencies
Uses POSIX make/sh, C compiler, awk, sed, diff, tar, gzip, lzip, curl, git, gpg, zic/zdump/date sources, tz data files, AWK scripts, and manual-page tooling.

## Behavior/Risks
Encodes many policy switches: leap-second install topology, backward links, packrat backzone data, generated data forms, timestamp reproducibility, character-set validation, zone table validation, future-transition checks, and alternate `time_t` builds. Build/install behavior is highly parameterized and sensitive to host tool compatibility.
