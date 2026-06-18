# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/makefile.cfg

This is the configurable makefile template for IJG JPEG. `configure` substitutes `@...@` variables to produce the actual `Makefile`.

It defines installation directories, compiler and linker settings, libtool controls, library versioning, memory-manager backend selection, and basic tool commands. `LIBTOOL`, `O`, and `A` switch object/archive suffixes between libtool and ordinary builds.

The file enumerates source groups: JPEG library sources, system-dependent memory backends, application sources, headers, documentation, make/config files, configure support files, miscellaneous support files, and test images. The listed files in this research group appear in these source/object sets: `jquant1.c`, `jquant2.c`, `jutils.c`, `jversion.h`, `rdcolmap.c`, `rdgif.c`, `rdbmp.c`, `rdjpgcom.c`, `ltconfig`, and `ltmain.sh`.

Build targets include `all`, `ansi2knr`, `libjpeg.a`, `libjpeg.la`, `cjpeg`, `djpeg`, `jpegtran`, `rdjpgcom`, and `wrjpgcom`. Installation targets install programs, man pages, the library, and public headers. Cleaning targets remove objects, generated libraries, tools, config outputs, and libtool directories.

The `test` target performs round-trip and transform checks with the sample images, comparing generated outputs to expected files. The `jconfig.h` target is a deliberate failure path reminding users to prepare system-dependent configuration if configure has not produced it.

The bottom section is explicit dependency metadata for every object file. This makefile is build orchestration for the vendored JPEG distribution.
