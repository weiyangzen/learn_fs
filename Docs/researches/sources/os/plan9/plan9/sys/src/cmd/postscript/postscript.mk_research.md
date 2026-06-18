# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postscript.mk

Top-level makefile for the Plan 9/DWB PostScript support package.

Key responsibilities:
- Documents package-wide configuration variables and build/install workflows.
- Defines global defaults:
  - `SYSTEM=V9`
  - `VERSION=3.3.2`
  - owner/group
  - root, font, host font, manpage, PostScript binary/library, and tmac directories
  - compiler/linker flags
  - Datakit options
  - `ROUNDPAGE=TRUE`
- Defines default `TARGETS` for the full PostScript tool suite, including `postdaisy`, `postdmd`, `postgif`, `postio`, `postmd`, `postprint`, and `postreverse`.
- Provides aggregate `all`, `clean`, `clobber`, `install`, and `changes` targets.
- Recursively invokes each target directory’s `<target>.mk` when the directory and makefile exist.

Integration:
- Exports package-level variables into recursive makes.
- Sets `COMMONDIR=../common` for subdirectories.
- Allows `TARGETS=...` override to build/install only selected tools.
- `changes` propagates selected configuration values into lower-level makefiles/manpages.

Risks and quirks:
- Historical makefile assumes `/bin/make`, privileged install paths, and recursive make behavior.
- Target list includes many directories beyond this group; nonexistent target directories are silently ignored by the shell test.
- Comments warn that source files must be updated after changing definitions by running `make -f postscript.mk changes`.
