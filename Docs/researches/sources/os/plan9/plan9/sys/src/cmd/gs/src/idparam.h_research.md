# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idparam.h

Interface for dictionary parameter helpers. It documents common return conventions:
- `0`: valid parameter found
- `1`: defaulted/missing parameter
- `<0`: error
- routines with `null` may return `2` for null

It declares scalar, array, procedure, matrix, UID, and UID-check helpers. It intentionally takes C string keys rather than static name refs to simplify GC handling.
