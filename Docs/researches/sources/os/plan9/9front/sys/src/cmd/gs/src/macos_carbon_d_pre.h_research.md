# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/macos_carbon_d_pre.h

## Purpose
CodeWarrior prefix header for the Mac OS Carbon debug target.

## Main Content
- Include guard `macos_carbon_d_pre_INCLUDED`.
- Defines `__CARBON__`.
- Defines `DEBUG 1` for verbose/debug Ghostscript builds.

## Integration Notes
- Selected by `macgenmcpxml.sh` when generating the Carbon debug target settings.

## Risks and Edge Cases
- Only build-time macro definitions; any behavior depends on source files checking `__CARBON__` and `DEBUG`.
