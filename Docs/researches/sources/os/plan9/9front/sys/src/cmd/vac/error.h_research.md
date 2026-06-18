# File Research: sources/os/plan9/9front/sys/src/cmd/vac/error.h

`error.h` declares the vac error-string globals and undefines `EIO` first to avoid collisions with host `<errno.h>` on Mac OS X. It is included by vac implementation files that need shared textual error identifiers.
