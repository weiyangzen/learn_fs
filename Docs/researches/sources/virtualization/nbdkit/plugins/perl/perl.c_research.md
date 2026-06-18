# File Research: sources/virtualization/nbdkit/plugins/perl/perl.c

## Purpose
Implements the `perl` plugin adapter, embedding a Perl interpreter and forwarding nbdkit callbacks to functions defined by a user-supplied Perl script.

## Main Entry Points
- `perl_load()` initializes the embedded interpreter.
- `perl_config()` requires the first parameter to be `script=...`, parses/runs the script, verifies required callbacks, and forwards later config to Perl `config`.
- `callback_defined()` checks if a named Perl subroutine exists.
- `check_perl_failure()` converts Perl `$@` exceptions into nbdkit errors.
- XS functions expose `Nbdkit::debug`, `Nbdkit::set_error`, and constants.
- Callback wrappers implement config_complete, get_ready, open/close, get_size, capability checks, pread, pwrite, zero, flush, and trim.

## Internal Mechanics
The adapter stores one global `PerlInterpreter *`. `open` returns an `SV *` copied with `newSVsv`; nbdkit passes it back as the handle, and `close` decrements its refcount. The plugin uses `THREAD_MODEL_SERIALIZE_ALL_REQUESTS`, avoiding parallel Perl callback execution. Missing write/flush/trim/zero callbacks are handled with nbdkit-like fallback behavior.

## Dependencies
Uses Perl embedding/XS APIs, nbdkit plugin API v2, and common cleanup helpers.

## Risks and Notes
The adapter exposes an older callback surface than the OCaml/Python adapters in this group: no extents/cache/list_exports wrappers are present. Large offsets/counts are passed through `newSViv`/`SvIV`, which can be sensitive to Perl integer width. `last_error` is a global used by zero fallback, but all requests are serialized, reducing concurrency risk.
