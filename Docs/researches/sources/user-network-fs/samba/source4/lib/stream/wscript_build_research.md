# sources/user-network-fs/samba/source4/lib/stream/wscript_build

## Purpose

This waf script defines the `LIBPACKET` subsystem that builds the packet framing helper.

## Important APIs, Types, and Functions

It declares `bld.SAMBA_SUBSYSTEM('LIBPACKET', source='packet.c', deps='LIBTLS')`.

## Control Flow

At build time, waf compiles `packet.c` into `LIBPACKET` and ensures `LIBTLS` is available before linking consumers.

## State and Persistence Behavior

No runtime state is present. The declaration affects generated build metadata.

## Dependencies and Integration Points

The explicit `LIBTLS` dependency reflects packet users that may operate over TLS-wrapped stream behavior, especially unreliable select handling.

## Risks and Edge Cases

If `packet.c` is used without direct TLS symbols, this dependency can still pull TLS-related build requirements into consumers. Build graph changes should confirm this remains intentional.

## Test Signals

Clean waf builds of `LIBPACKET` and consumers are the relevant signals.
