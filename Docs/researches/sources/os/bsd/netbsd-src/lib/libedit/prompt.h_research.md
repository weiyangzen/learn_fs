# File Research: sources/os/bsd/netbsd-src/lib/libedit/prompt.h

## Purpose
Private prompt subsystem declarations.

## Main Contents
Defines prompt state fields through the broader libedit headers and declares:
- `prompt_print`
- `prompt_init`
- `prompt_end`
- `prompt_set`
- `prompt_get`

## Integration
Prompt state is used by `refresh.c` for every redraw, by public `el_set`/`el_get` prompt operations, and by readline compatibility prompt wrappers.

## Risks And Notes
Prompt functions sit on the refresh path. Any callback or width-accounting change has immediate terminal-rendering impact.
