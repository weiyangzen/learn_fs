# File Research: sources/virtualization/nbdkit/filters/fua/fua.c

Implements a policy filter for Force Unit Access semantics. Configuration supports `fua-mode`/`fuamode` values `none`, `emulate`, `native`, `force`, `pass`, and `discard`, plus `flush-on-close`.

`fua_prepare()` validates that requested behavior is possible: emulation requires flush support; native/force require FUA support; flush-on-close requires flush support. In readonly mode the filter has no behavioral impact.

`fua_can_flush()` and `fua_can_fua()` report capabilities according to the selected mode. `update_flags()` rewrites FUA flags for `pwrite`, `trim`, and `zero`: emulate strips FUA and follows success with flush; force adds FUA; discard strips FUA; pass/native leave flags unchanged.

`fua_flush()` can pass through, no-op because every write used FUA, or deliberately discard flushes. `fua_finalize()` optionally flushes on close.
