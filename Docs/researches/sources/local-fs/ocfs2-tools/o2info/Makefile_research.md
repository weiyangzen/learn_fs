# File Research: sources/local-fs/ocfs2-tools/o2info/Makefile

This makefile builds the `o2info` binary and a local static helper archive `libo2info.a`. The executable links `o2info.c`, `operations.c`, and `utils.c` with `libocfs2`, `libtools-internal`, `com_err`, AIO libraries, and the local helper library.

It installs/generates the `o2info.1` manpage and distributes source, headers, and the manpage template. Build flags use strict warnings with `-Wno-format`, include the repository `include` directory plus the local directory, and define `VERSION`.

The notable integration detail is that `libo2info.c` is separated into `libo2info.a`, while the CLI links that archive back into `o2info`.
