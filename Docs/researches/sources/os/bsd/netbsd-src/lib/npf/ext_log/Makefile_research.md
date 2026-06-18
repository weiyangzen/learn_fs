# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_log/Makefile

## Summary
Builds the NPF `ext_log` module.

## Main Responsibilities
- Sets `MOD=ext_log`.
- Includes shared `../mod.mk`.

## Integration Notes
The shared make fragment determines source naming, library/module mode, install path, and libnpf dependency.
