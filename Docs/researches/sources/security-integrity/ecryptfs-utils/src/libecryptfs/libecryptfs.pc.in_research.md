# sources/security-integrity/ecryptfs-utils/src/libecryptfs/libecryptfs.pc.in

## Purpose
Template for the installed `libecryptfs.pc` pkg-config metadata. It lets external programs discover include flags, keyutils flags, library search path, and the package version for libecryptfs.

## Important APIs, types, and functions
- `prefix`, `exec_prefix`, `libdir`, and `includedir` are configure-time substitutions.
- `Name`, `Description`, and `Version` identify the package.
- `Cflags` emits the include directory and `@KEYUTILS_CFLAGS@`.
- `Libs` emits `@KEYUTILS_LIBS@`, `-L${libdir}`, and `-lecryptfs`.

## Control flow
No runtime flow. Configure substitutes variables, installation places the generated file where pkg-config can find it, and downstream builds query it.

## State and persistence behavior
Persists build metadata as an installed text file. It does not represent runtime eCryptfs state.

## Dependencies and integration points
Integrated by `Makefile.am` via `pkgconfig_DATA`. Consumers of libecryptfs use this file instead of hand-coding compiler and linker flags.

## Risks and edge cases
The template exposes keyutils flags but not all crypto/NSS flags visible in the library build; downstream static or unusual link modes may need additional private libs. If include installation layout diverges from `${includedir}`, consumers will compile against missing headers.

## Test signals
After installation, `pkg-config --modversion libecryptfs`, `--cflags`, and `--libs` should return substituted values. A minimal external program including `ecryptfs.h` and linking a libecryptfs symbol is the best end-to-end check.
