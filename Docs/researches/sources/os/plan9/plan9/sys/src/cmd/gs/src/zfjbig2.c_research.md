# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfjbig2.c

## Purpose
Implements interpreter support for `JBIG2Decode` and parsed JBIG2 global contexts.

## Key Functions
- `z_jbig2decode()` creates the JBIG2 decode filter and attaches an optional parsed global context.
- `z_jbig2makeglobalctx()` builds a `Jbig2GlobalCtx` from bytes and wraps it in an interpreter `astruct`.
- `jbig2_global_data_finalize()` releases the external JBIG2 global context.

## Important Behavior
- JBIG2 global context memory is not directly GC-managed, so a finalizer frees it.
- Invalid or unparseable global data returns `unknownerror`.

## Research Notes
PostScript code is expected to resolve `JBIG2Globals` and call `.jbig2makeglobalctx` before invoking the filter.
