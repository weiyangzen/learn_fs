# sources/user-network-fs/samba/source4/librpc/dcerpc.pc.in

## Purpose

This pkg-config template describes the installed DCE/RPC client library for external or higher-level build consumers.

## Important Fields

It exposes `Name: dcerpc`, description `DCE/RPC client library`, version `@PACKAGE_VERSION@`, and dependencies `ndr samba-util`. Link flags add `@LIB_RPATH@`, `${libdir}`, `-ldcerpc`, and `-ldcerpc-binding`. Cflags add `${includedir}` and `-DHAVE_IMMEDIATE_STRUCTURES=1`.

## Control Flow And State

There is no runtime flow. Configure/build substitution fills prefix, exec prefix, libdir, includedir, version, and RPATH placeholders.

## Dependencies And Integration Points

Consumers that use pkg-config inherit the NDR and Samba utility dependencies and link against the core DCE/RPC client and binding libraries. The `HAVE_IMMEDIATE_STRUCTURES` define affects generated header expectations for immediate struct layout support.

## Risks

Incorrect library names or missing requirements break downstream builds. Public flag changes here are externally visible and should be treated as compatibility-impacting.

## Test Signals

After installation, `pkg-config --libs --cflags dcerpc` should emit usable flags, and a small program including DCE/RPC headers and linking against `dcerpc` should compile.
