# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postbgi/postbgi.mk

Makefile for the `postbgi` translator.

Key responsibilities:
- Defines build/install variables for binary, prologue library, and man page.
- Builds `postbgi` from `postbgi.o` and common `glob`, `misc`, and `request` objects, linking math library.
- Installs binary, `postbgi.ps` prologue, and man page.
- Delegates common object builds to `../common/common.mk`.
- Provides a `changes` target to rewrite defaults and update man-page prologue path.

Notable behavior:
- Creates both `POSTBIN` and `POSTLIB` directories during install if needed.
