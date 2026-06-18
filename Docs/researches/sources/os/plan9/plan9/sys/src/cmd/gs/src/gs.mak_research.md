# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gs.mak

Purpose: Generic Ghostscript makefile fragment included by platform-specific makefiles.

Key definitions: documents required platform variables, normalizes generated/object directories for bundled libraries, defines executable and auxiliary tool paths, declares generated headers, and builds generated `.dev`, `ld.tr`, `obj.tr`, and `gconfigd.h` files.

Control flow: `all/default` depend on `$(GS_XE)`. `clean`, `mostlyclean`, and `config-clean` remove generated objects, devices, config headers, helper executables, and temporary files. Device and feature lists are assembled into `devs.tr` using `echogs`; `genconf` turns those into configuration/linker/object tables; `gconfigd.h` records runtime defaults such as library paths, cache dir, doc dir, init file, revision, and revision date.

Dependencies: Requires platform makefiles to define compiler/linker/tool commands, paths, devices, features, third-party source locations, and deletion/copy utilities. Depends heavily on `echogs`, `genconf`, and generated `.dev` files.

Risks and notes: Comments mark some clean rules as not subsystem-specific. Many feature/device lists are spread over numbered variables, so platform makefiles must maintain ordering and line-length constraints carefully.
