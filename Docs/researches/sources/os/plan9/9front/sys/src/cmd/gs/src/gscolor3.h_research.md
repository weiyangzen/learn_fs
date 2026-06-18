# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor3.h

## Role

`gscolor3.h` declares the client interface for LanguageLevel 3 smooth shading operations.

This is rendering/color API infrastructure, not filesystem code.

## Public API

- `gs_setsmoothness`
- `gs_currentsmoothness`
- `gs_shfill`

## Dependencies

Forward-declares `gs_shading_t` when needed.

## Notable Risks

Header-only; implementation is in `gscolor3.c`.
