# File Research: sources/os/bsd/freebsd-src/sbin/ipf/Makefile

## Purpose
Top-level build orchestration for FreeBSD `sbin/ipf`.

## Main Elements
- Includes `src.opts.mk`.
- Builds `libipf` first, then `ipf`, `ipfstat`, `ipmon`, `ipnat`, and `ippool`.
- Adds `ipfs` only when `MK_IPFILTER_IPFS != "no"`.
- Leaves `ipftest`, `ipresend`, and `ipsend` temporarily disconnected.
- Enables subdirectory parallelism.

## Dependencies And Integration
Integrates the IPFilter userland programs with the FreeBSD build option framework.

## Risk Notes
Build membership is controlled here; disabling or omitting a subdir silently removes an IPFilter utility from the base build.
