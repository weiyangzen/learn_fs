# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gendev.c

Build-time `.dev` file generator. It creates per-module `.dev` fragments from command-line category/item pairs.

Key behavior:
- Accepts device, module, and append modes through `-d`, `-m`, and `-a`.
- Supports name-prefix and file-prefix switches for generated symbols and object paths.
- Writes include-guarded `.dev` output containing category-specific macro calls.
- Handles categories such as `dev`, `dev2`, `emulator`, `font`, `include`, `init`, `iodev`, `lib`, `obj`, `oper`, and `ps`.
- Uses a `RES_SCAN` pass to handle `uniq_last` semantics for libraries, recording the last contributing file/item marker.

Notable dependencies:
- Standalone C build tool using standard headers and Ghostscript `stdpre.h`.

Research notes:
- Comments note unimplemented behaviors: no `-replace` handling and no merge of `device` and `device2`.
- The generated output is consumed by `genconf.c` and the build system.
