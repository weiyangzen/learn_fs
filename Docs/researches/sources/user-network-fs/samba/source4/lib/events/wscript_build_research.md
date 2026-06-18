# sources/user-network-fs/samba/source4/lib/events/wscript_build

## Purpose

This waf script declares the private Samba4 `events` library.

## Important APIs, Types, and Functions

It calls `bld.SAMBA_LIBRARY()` for `events`, with source `tevent_s4.c`, private dependency `samba-util`, public dependency `tevent`, and `private_library=True`.

## Control Flow

At build time it registers the library so internal Samba4 targets can link `s4_event_context_init()`.

## State and Persistence Behavior

There is no runtime state. It persists library metadata in the waf build graph.

## Dependencies and Integration Points

It connects the local Samba4 event wrapper to tevent and Samba utility support.

## Risks and Edge Cases

Because the library is private, external code should not rely on it. Public dependency visibility must keep tevent headers available for consumers.

## Test Signals

Signals are successful build/link of internal event users and runtime service startup that creates Samba4 event contexts.
