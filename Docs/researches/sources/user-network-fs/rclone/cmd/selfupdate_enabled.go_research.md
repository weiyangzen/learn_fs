# sources/user-network-fs/rclone/cmd/selfupdate_enabled.go

## Purpose

This file exposes the command-package feature flag for normal self-update-capable builds.

## Important APIs, Types, and Functions

`const selfupdateEnabled = true` is defined in package `cmd`.

## Control Flow

There is no runtime flow. It enables command registration/help logic to use a compile-time feature flag without importing the selfupdate subpackage.

## State and Persistence Behavior

No state is stored.

## Dependencies and Integration Points

The build tag is `!noselfupdate`. The comment documents that the constant must remain in `cmd` to prevent dependency loops.

## Risks and Test Signals

Risks are limited to build configuration and accidental relocation. Tagged build tests are the relevant signal.
