# File Research: sources/virtualization/nbd/tests/code/punchdummy.c

## Purpose
Provides a dummy `punch_hole()` implementation for tests that link server helpers but do not expect hole punching to be called.

## Behavior
Defines `punch_hole()` to call `g_assert_not_reached()`.

## Dependencies
Includes GLib and `backend.h`.

## Risks and Notes
This is a link stub, not production behavior. Tests using it will fail if the code path unexpectedly calls `punch_hole()`.
