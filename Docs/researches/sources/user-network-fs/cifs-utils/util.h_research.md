# sources/user-network-fs/cifs-utils/util.h

## Purpose
`util.h` declares the cifs-utils portability helpers implemented in `util.c`.

## Important APIs
The public functions are `strlcpy`, `strlcat`, and `getusername`. The first two may map either to local replacements or platform functions depending on configure results; `getusername` maps a UID to a passwd username.

## Control flow and state
The header has no runtime flow or persistence. It forms an include contract for utility consumers.

## Dependencies and integration points
The declarations use `size_t` and `uid_t` but the header does not include `<stddef.h>` or `<sys/types.h>`, relying on includers to provide those types. It is included by `util.c` after the needed system headers.

## Risks
Standalone inclusion can fail under strict compilation because required typedefs are not self-contained. Declaring `strlcpy`/`strlcat` unconditionally can conflict if a platform prototype with different visibility is already present, although configure guards implementation emission.

## Test signals
Add a compile-only test that includes `util.h` first in a translation unit. Build with strict warnings on platforms with and without native `strlcpy`/`strlcat`.
