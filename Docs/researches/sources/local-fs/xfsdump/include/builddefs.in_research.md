# File Research: sources/local-fs/xfsdump/include/builddefs.in

`builddefs.in` is an autoconf-substituted make include that centralizes package metadata, tool paths, library paths, platform flags, gettext settings, and shared build rules.

Key variables:
- Build mode: `DEBUG`, `OPTIMIZER`, `CFLAGS`, `LOADERFLAGS`, `MALLOCLIB`.
- Libraries: `LIBRMT`, `LIBXFS`, `LIBATTR`, `LIBPTHREAD`, `LIBUUID`, `LIBCURSES`, `LIBHANDLE`.
- Package metadata: name, user/group, release, version, platform, distribution.
- Install paths: sbin, root sbin, root lib, include, man, docs, locale.
- Tools: compiler, awk, sed, tar, zip, make, sort, shell, libtool, makedepend, gettext utilities, rpm tooling.
- Feature toggles: curses, shared libs, gettext, zipped manpages, fallocate.

Platform behavior:
- Linux sets `_GNU_SOURCE`, `_FILE_OFFSET_BITS=64`, and `__linux__` dependency flags.
- Darwin, IRIX, and FreeBSD get platform-specific preprocessor/linker settings.

Important build rule:
- `CFLAGS` is assembled from external flags, generated global flags, platform flags, and local flags.
- Includes `buildmacros` and defines `_FORCE` for always-rebuilt targets.
