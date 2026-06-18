<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit.go -->
# sources/user-network-fs/rclone/fs/accounting/tpslimit.go

## Purpose

`tpslimit.go` implements a global transactions-per-second limiter, typically used by HTTP transaction paths.

## Important APIs, Types, and Functions

Global `tpsBucket` is a `*rate.Limiter`. `StartLimitTPS(ctx)` creates it when `ConfigInfo.TPSLimit` is positive, using `TPSLimitBurst` or at least one. `LimitTPS(ctx)` waits on the limiter and logs non-cancel errors.

## Control Flow

Accounting startup calls `StartLimitTPS`. Transaction paths call `LimitTPS` before making requests; if no limiter exists, the call is a no-op.

## State and Persistence Behavior

State is process-global and in memory. Starting multiple times can replace the limiter.

## Dependencies and Integration Points

It depends on `fs.ConfigInfo`, logging, and `golang.org/x/time/rate`. It complements bandwidth limiting but controls request rate rather than bytes.

## Risks and Test Signals

Risks include global state leakage across tests, context cancellation behavior, and unexpected serialization of unrelated backends. Tests should verify timing with configured limits and no-op behavior when disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit.go -->
