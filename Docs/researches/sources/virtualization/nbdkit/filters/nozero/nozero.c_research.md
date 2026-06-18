# File Research: sources/virtualization/nbdkit/filters/nozero/nozero.c

This filter controls advertised and executed write-zeroes behavior. `zero-mode` / `zeromode` accepts `none` (default), `emulate`, `notrim`, and `plugin`; `fast-zero-mode` / `fastzeromode` accepts `default`, `none`, `slow`, and `ignore`.

`.prepare` validates modes that require backend zero support (`notrim` and `plugin`) unless the connection is readonly. `.can_zero` advertises no zero support, nbdkit emulation, or the backend's capability depending on mode. `.can_fast_zero` either delegates to the backend in default plugin modes or reflects the local fast-zero policy.

The `.zero` handler is reached only when zero operations are delegated to the backend. It may reject fast-zero with `ENOTSUP`, silently clear the fast-zero flag, or remove `MAY_TRIM` for `notrim`, then calls `next->zero`.

Edge cases are centered on capability consistency: `zero-mode=plugin` requires backend support, `zero-mode=none` suppresses zero requests, and `fast-zero-mode=ignore` intentionally turns a requested fast zero into a potentially slow zero.
