# File Research: sources/virtualization/nbdkit/plugins/ocaml/plugin.c

## Purpose
Implements the core OCaml-to-nbdkit plugin adapter. It initializes the OCaml runtime, receives plugin registration from OCaml code, stores OCaml callbacks as GC roots, and translates nbdkit C callbacks into OCaml function calls.

## Main Entry Points
- `plugin_init()` starts OCaml, releases the runtime lock, initializes thread tracking, verifies OCaml called `NBDKit.register_plugin`, and returns the constructed `nbdkit_plugin`.
- `ocaml_nbdkit_set_string_field()` sets plugin metadata strings such as name, version, description, config help, and magic config key.
- `ocaml_nbdkit_set_field()` assigns callback wrappers and roots the OCaml callback values.
- Wrapper functions cover load/unload, config, thread model, get-ready, after-fork, cleanup, preconnect, export listing/default export, open/close, size, capabilities, block size, pread/pwrite, flush, trim, zero, extents, and cache.
- `exception_to_error()` maps OCaml exceptions into nbdkit error messages and errno where possible.

## Internal Mechanics
The adapter holds one `value <callback>_fn` per supported callback. Per-connection handles are heap objects containing an OCaml value rooted with `caml_register_generational_global_root`. I/O buffers are exposed to OCaml as bigarrays wrapping nbdkit-owned memory. For OCaml 5, thread-local state registers non-main nbdkit worker threads with the OCaml runtime and unregisters them at thread teardown. `after_fork_wrapper()` invokes OCaml runtime atfork handling after real forks.

## Dependencies
Uses OCaml runtime, callbacks, bigarrays, exception formatting, thread APIs, pthread TLS, nbdkit plugin API v2, and `callbacks.h` macro expansion.

## Risks and Notes
Every callback must acquire the OCaml runtime lock, so the declared nbdkit thread model can allow parallel nbdkit calls while OCaml execution remains runtime-serialized as appropriate. `block_size_wrapper()` appears to assign `*maximum = i` after validating `i64`; `i` still contains the preferred block size, so non-`-1` maximum block sizes can be reported incorrectly. `pwrite_wrapper()` casts away `const` when wrapping the input buffer as a bigarray, so OCaml code could mutate a buffer that should be read-only. Error conversion is best-effort and callback exceptions in close/unload paths are logged but cannot fully recover.
