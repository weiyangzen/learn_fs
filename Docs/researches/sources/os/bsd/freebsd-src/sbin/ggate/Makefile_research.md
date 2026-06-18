# File Research: sources/os/bsd/freebsd-src/sbin/ggate/Makefile

## Purpose

Top-level subdirectory Makefile for GEOM Gate utilities.

## Build Definition

Builds subdirectories:
- `ggatec`
- `ggated`
- `ggatel`

Includes `<src.opts.mk>` and `<bsd.subdir.mk>`.

## Integration Notes

This file only orchestrates child utility builds; functionality lives in child directories and shared ggate sources.
