# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/jpeg.mak

## Identity

- Lines/bytes: 389 lines, 15,307 bytes.
- SHA-256: `9370e13f9264ac848912d90782e5fbe8ba602227e376e255cea300d9e00c8f68`.
- Role: Ghostscript makefile fragment for building or sharing the IJG JPEG library.

## Inputs And Build Variables

Callers must define:

- `GSSRCDIR`, `JSRCDIR`, `JGENDIR`, `JOBJDIR`.
- `JVERSION`.
- `SHARE_JPEG`: `0` for private build, `1` for shared library use.
- `JPEG_NAME` for shared JPEG library mode.

Derived paths include `JSRC`, `JGEN`, `JOBJ`, `JO_`, and `JPEG_MAK`.

## Header Generation

The makefile creates Ghostscript-controlled JPEG headers:

- `jconfig0.h` from `stdpn.h`, `stdpre.h`, and `gsjconf.h`.
- `jconfig1.h` as a wrapper that includes system `jconfig.h`.
- `jconfig_.h` selected from `jconfig$(SHARE_JPEG).h`.
- `jmorecf0.h` from `gsjmorec.h`.
- `jmorecf1.h` as a wrapper that includes system `jmorecfg.h`.
- `jmorecfg.h` from `jmorecf0.h`.
- `jmcorig.h` from IJG’s original `jmorecfg.h`.
- `jpeglib0.h` from IJG’s `jpeglib.h`.
- `jpeglib1.h` as a wrapper around system `jpeglib.h`.
- `jpeglib_.h` selected from `jpeglib$(SHARE_JPEG).h`.

## Build Strategy

The makefile copies IJG `.c` files into Ghostscript’s generated directory before compiling them, then deletes the temporary copies. The comments explain the reason: C compilers disagree on whether quoted includes search the source file’s directory before `-I` paths, so copying ensures IJG files include Ghostscript’s modified headers.

## Modules Built

Common module:

- `jpegc0.dev`: `jcomapi`, `jutils`, `jmemmgr`, `jerror`.

Compression module:

- `jpege.dev` chooses shared or private mode.
- Private `jpege6.dev` includes common code and encoder objects such as `jcapimin`, `jcapistd`, `jcinit`, `jccoefct`, `jccolor`, `jcdctmgr`, `jchuff`, `jcmainct`, `jcmarker`, `jcmaster`, `jcparam`, `jcprepct`, `jcsample`, and `jfdctint`.

Decompression module:

- `jpegd.dev` chooses shared or private mode.
- Private `jpegd6.dev` includes common code and decoder objects such as `jdapimin`, `jdapistd`, `jdinput`, `jdphuff`, `jdcoefct`, `jdcolor`, `jddctmgr`, `jdhuff`, `jdmainct`, `jdmarker`, `jdmaster`, `jdpostct`, `jdsample`, and `jidctint`.

## Behavior And Integration

- Supports IJG versions 6, 6a, and 6b, with version 6b treated as current in the comments.
- In shared mode, generated `.dev` files refer to `JPEG_NAME` as a library.
- In private mode, Ghostscript compiles selected IJG source files with modified headers.
- Cleaning removes JPEG object files and generated `jpeg*.dev` files.

## Research Notes

- This is the central explanation for why several duplicate/generated-looking JPEG headers exist in this directory.
- The build is conservative: all IJG objects depend on the few headers Ghostscript may alter.
- No Plan 9 filesystem behavior is implemented here; this is application build plumbing for Ghostscript.
