# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/macos-fw.mak

`macos-fw.mak` is a partial makefile for building Ghostscript as a Mac OS X/Darwin shared object and framework. It defines shared-object build directories, loader names, `.dylib` naming, versioned symlinks, and framework packaging paths.

The shared-library targets create `lib$(GS).$(major).$(minor).dylib` and symlink major and unversioned names to it. `SODEFS` drives a recursive make with dynamic-library linker flags, shared-object output directories, callout stdio, display-device selection, and relocated generated/object directories.

Targets include `so`, `sodebug`, `install-so`, `soinstall`, `framework`, `framework_install`, `SODIRS`, and `soclean`. The framework target lays out `Versions/<version>`, `Headers`, `Resources`, top-level symlinks, bundled PostScript resources, man pages, docs, and selected public headers.

This file is included by `macosx.mak`. It assumes Darwin shell tools like `ln`, `cp`, `mkdir`, and `rm`, and comments note that the install name is framework-oriented, making plain `.dylib` use less clean than framework use.
