# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gscpm.h

## Purpose
Defines charpath modes and cachedevice status values.

## Key Contents
- `gs_char_path_mode`:
  - normal show,
  - charwidth,
  - false/true charpath,
  - false/true charboxpath.
- `gs_in_cache_device_t`:
  - no cachedevice,
  - cachedevice not caching,
  - not caching with clip,
  - actively caching.

## Important Details
- Default values are explicitly required to be zero for both enums.

## Research Notes
This is a small shared state-definition header for text/path/cachedevice code elsewhere.
