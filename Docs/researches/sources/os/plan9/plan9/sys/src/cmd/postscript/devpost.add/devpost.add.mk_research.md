# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/devpost.add/devpost.add.mk

Makefile for installing additional `devpost` font files.

Key responsibilities:
- Defines install ownership, group, and font directory.
- Creates `$(FONTDIR)` and `$(FONTDIR)/devpost` if needed.
- Copies `FONTFILES` into `devpost`.
- Provides a `changes` target to rewrite makefile defaults.

Notable behavior:
- `FONTFILES` defaults to `??`, expecting caller/site customization.
