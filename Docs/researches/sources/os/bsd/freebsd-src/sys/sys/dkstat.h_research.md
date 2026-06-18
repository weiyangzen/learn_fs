# File Research: sources/os/bsd/freebsd-src/sys/sys/dkstat.h

## Purpose
Compatibility header for disk statistics-related consumers.

## Main Elements
- Contains licensing/header guard.
- Includes `sys/resource.h`.

## Dependencies And Integration
Provides a legacy include name for code expecting `<sys/dkstat.h>`.

## Risk Notes
This header does not define disk statistics structures itself; consumers need the actual resource/devstat interfaces for data.
