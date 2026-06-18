# sources/user-network-fs/rclone/cmd/selfupdate_disabled.go

## Purpose

This file exposes the command-package feature flag for builds compiled with `noselfupdate`.

## Important APIs, Types, and Functions

`const selfupdateEnabled = false` is defined in package `cmd`.

## Control Flow

There is no runtime flow. Other command code can branch on the constant and the compiler can eliminate dead paths.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `noselfupdate`. The constant intentionally lives in `cmd`, not `cmd/selfupdate`, to avoid an import cycle.

## Risks and Test Signals

The risk is build-tag drift: all call sites must compile under both enabled and disabled variants. The main signal is successful tagged compilation, not runtime tests.
