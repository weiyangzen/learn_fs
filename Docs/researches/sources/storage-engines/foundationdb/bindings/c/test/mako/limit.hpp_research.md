# sources/storage-engines/foundationdb/bindings/c/test/mako/limit.hpp

## Purpose
Portability shim for platform path-limit headers used by Mako.

## Important APIs, types, and functions
Includes `<linux/limits.h>` on Linux, `<sys/syslimits.h>` on Apple platforms, and `<limits.h>` elsewhere.

## Control flow
Only compile-time preprocessor selection exists.

## State and persistence behavior
No runtime state or persistence.

## Dependencies and integration points
Provides constants such as `PATH_MAX` to Mako code across supported platforms.

## Risks and test signals
Unusual platforms may lack expected constants in the fallback header. Compile failure is the signal.
