# File Research: sources/windows/reactos/drivers/filesystems/udfs/CMakeLists.txt

## Purpose

This CMake file builds the ReactOS UDFS filesystem driver module.

## Main Contents

- Adds `Include` to the include path.
- Builds a `udfs` module from UDF core files, UDF info/physical/remap files, cache/memory/debug helpers, dispatch handlers, and `udffs.h`.
- Adds `udffs.rc` as the resource file.
- Defines `_CRT_NON_CONFORMING_SWPRINTFS`.
- Suppresses selected GCC/Clang warnings for this legacy codebase.
- Configures the target as a kernel-mode driver with `set_module_type(udfs kernelmodedriver)`.
- Links `${PSEH_LIB}` and imports `ntoskrnl` and `hal`.
- Adds precompiled header `udffs.h`.
- Installs the driver to `reactos/system32/drivers`.
- Registers `udfs_reg.inf`.

## Integration Notes

This is the build entry point for the UDFS driver under ReactOS. It intentionally omits `pnp.cpp` via a commented source entry, so PnP behavior is either not built or handled elsewhere.

## Risks And Edge Cases

- The warning suppressions indicate legacy code patterns that may hide real portability problems.
- `udffs.h` is both listed as a source and used as PCH, so changes to it have broad rebuild impact.
- `pnp.cpp` being commented out is a functional build decision worth checking before adding PnP-related changes.
