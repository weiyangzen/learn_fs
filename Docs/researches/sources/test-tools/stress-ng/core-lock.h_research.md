# sources/test-tools/stress-ng/core-lock.h

## Purpose

This header exposes the generic lock pool and lock-handle API.

## Important APIs, Types, And Functions

It declares shared lock memory map/unmap plus create, destroy, acquire, relaxed acquire, and release functions. Lock handles are opaque `void *` values.

## Control Flow

Callers must map lock memory before creating locks, then create handles, use acquire/release around shared state, destroy handles, and unmap during shutdown.

## State And Persistence Behavior

The implementation stores locks in shared anonymous memory and may create kernel semaphore state depending on selected primitive.

## Dependencies And Integration Points

The API supports shared-memory subsystems such as warn-once and metrics synchronization.

## Risks And Test Signals

The lifecycle order is critical. Tests should verify create fails before mapping and that destroy/release reject invalid handles.
