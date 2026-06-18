# File Research: sources/os/plan9/9front/sys/src/9/port/devcap.c

Purpose: capability authentication device `#¤`, allowing privileged code to register SHA1 HMAC hashes and users to consume a matching capability to change process user.

Exposed interface: directory with `capuse` and `caphash`. `caphash` is write-only and eve-only; `capuse` accepts capability strings. Eve can remove `caphash` from the directory via `remove`, reducing exposure after setup.

Core implementation: `capalloc` holds a qlocked linked list of `Caphash` records with tick timestamps. `addcap` appends a hash after trimming expired/excess entries. `remcap` trims, finds a hash with `tsmemcmp`, removes it, and returns it for single-use consumption. Limits are `Maxhash` 256 and `Timeout` 60 seconds.

Capability format: writes to `capuse` are copied into secure memory, split at the final `@` into identity string and key, HMAC-SHA1 is computed, and optional `from@to` syntax requires `from` to match `up->user`. On success `procsetuser(to)` is called.

Dependencies: `libsec.h` SHA1/HMAC and secure allocation.

Research notes: this is security-sensitive. The code uses time-safe hash comparison and one-shot removal, but review should focus on capability string grammar, error paths that retain allocated secure memory until unwound, and the trust boundary of eve-only `caphash`.
