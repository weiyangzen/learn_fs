# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/dwmain.h

## Role
Small shared Win32 launcher header.

## Contents
- Defines resource icon IDs `GSTEXT_ICON` and `GSIMAGE_ICON`.
- Declares external `HWND hwndtext`.

## Important Interfaces
- `hwndtext` shared by image code for forwarding key and drag/drop input to the text window.

## Dependencies And Coupling
- Requires `HWND` from Win32 headers before inclusion.
- Used by `dwmain.c`, `dwimg.c`, and related Win32 sources.

## Risks And Notes
- Minimal global-state header.

## Filesystem Relevance
None.
