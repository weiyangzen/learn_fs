# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/local.h

## Purpose
Declares private shared YP libc symbols used across the YP client implementation.

## Contents
Declares `__yp_unbind()` and `_yp_invalid_domain()`, plus shared globals for timeout, error retry count, bind retry count, and cached default domain.

## Dependencies
Requires `struct dom_binding` from YP/RPC headers and NetBSD `__BEGIN_DECLS`/`__END_DECLS`.

## Risks And Notes
This header exposes mutable globals shared by the YP implementation, so retry and timeout behavior can be affected across calls.
