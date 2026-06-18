# sources/test-tools/stress-ng/test/test-libjpeg.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_JPEG` and link flags `-ljpeg` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `stdlib.h`, `string.h`, `jpeglib.h`. Defined functions: `main`. Referenced calls/builtins: `memset`, `jpeg_std_error`, `jpeg_create_compress`, `jpeg_stdio_dest`, `jpeg_set_defaults`, `jpeg_set_quality`, `jpeg_start_compress`, `jpeg_write_scanlines`, `jpeg_finish_compress`, `jpeg_destroy_compress`. Important structs/unions/enums: `jpeg_compress_struct`, `jpeg_error_mgr`. Important scalar/library types: `jpeg_error_mgr`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `memset`, `jpeg_std_error`, `jpeg_create_compress`, `jpeg_stdio_dest`, `jpeg_set_defaults`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `stdlib.h`, `string.h`, `jpeglib.h`; linker availability for `-ljpeg`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `HAVE_LIB_JPEG`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 56 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, stdlib.h, string.h, jpeglib.h.

- Calls/builtins detected: memset, jpeg_std_error, jpeg_create_compress, jpeg_stdio_dest, jpeg_set_defaults, jpeg_set_quality, jpeg_start_compress, jpeg_write_scanlines, jpeg_finish_compress, jpeg_destroy_compress.

- Structs/types detected: struct jpeg_compress_struct, struct jpeg_error_mgr, jpeg_error_mgr.
