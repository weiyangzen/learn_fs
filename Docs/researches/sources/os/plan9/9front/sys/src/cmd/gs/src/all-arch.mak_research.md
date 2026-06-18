# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/all-arch.mak

This is a large architecture-wrapper makefile for building Ghostscript across many historical Unix platforms, authored and maintained for University of Utah local build workflows. It delegates to Ghostscript Unix makefiles while supplying architecture-specific compilers, flags, library paths, and install conveniences.

Key responsibilities:
- Provides convenience targets such as `all`, `clean`, `mostlyclean`, `clobber`, `distclean`, `maintainer-clean`, `init`, and installation targets.
- Wraps Ghostscript makefiles through `ARGS = -f src/unixansi.mak` and `ARGSGCC = -f src/unix-gcc.mak`.
- Defines shared common arguments for device additions, search paths, JPEG/PNG/zlib source locations, and shared-library options.
- Sets local install/search paths, including extensive font directories in `GS_LIB_DEFAULT`.
- Adds local extra devices `st800` and `stcolor`.
- Defines many architecture targets: Rhapsody, DEC OSF, Ultrix, HP-UX, AIX, Linux, NeXT, IRIX, Solaris, and SunOS variants.
- Contains per-platform compiler workarounds, including no-optimization steps for specific SGI compiler/object issues.

Important build relationships:
- Uses `TARGETS` to pass either default or explicit child-make targets.
- Defaults `SHARE_LIBPNG=1` and `SHARE_ZLIB=1`, with source tree variables still available.
- `install-binary` removes the current `gs`, runs install with broad X library path coverage, then hard-links a versioned binary name.
- `install-fontmap` and `install-pdfsec` perform local post-install customization.

Notable implementation details and risks:
- This is site-specific historical build automation, not a generic distribution build path.
- Contains hard-coded `/usr/local` paths and redacted Utah host convenience targets.
- Uses old compiler assumptions and platform-specific flags that are unlikely to be useful on modern systems.
- No OS filesystem logic is implemented. It only coordinates builds and installs.
- Its value for research is provenance and build-surface mapping for embedded Ghostscript.

Research classification: historical multi-architecture Ghostscript build wrapper, mostly archival within the 9front source tree.
