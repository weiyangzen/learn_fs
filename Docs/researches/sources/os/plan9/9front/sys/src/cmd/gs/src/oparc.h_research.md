# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/oparc.h

## Purpose
Header declaring PostScript arc operator implementations.

## Main Content
- Include guard `oparc_INCLUDED`.
- Declares `zarc`, `zarcn`, and `zarct`, each taking `i_ctx_t *`.

## Integration Notes
- Comment explains these declarations are separate from `opextern.h` because arc operators are not included in PDF-only configurations.

## Risks and Edge Cases
- Requires `i_ctx_t` to be declared before inclusion.
