# sources/user-network-fs/samba/source4/librpc/dcerpc_samr.pc.in

## Purpose

This pkg-config template describes the installed SAMR-specific DCE/RPC client library.

## Important Fields

It exposes `Name: dcerpc_samr`, description `DCE/RPC client library - SAMR`, version `@PACKAGE_VERSION@`, and requires `dcerpc ndr ndr_standard`. Link flags add `-ldcerpc-samr`; Cflags add the include directory and `HAVE_IMMEDIATE_STRUCTURES`.

## Control Flow And State

The file is build-time metadata only. Template variables are substituted during installation.

## Dependencies And Integration Points

It layers SAMR generated client support on top of the generic DCE/RPC pkg-config module. Code such as `userman.c` depends on SAMR generated stubs internally; external consumers use this file to link against the installed SAMR client library.

## Risks

Because it exposes generated SAMR APIs, dependency drift between `dcerpc-samr`, `ndr_standard`, and installed headers can break consumers. The pkg-config name uses an underscore while the library uses a hyphen, which is intentional but easy to confuse in tooling.

## Test Signals

Installation tests should run `pkg-config --exists dcerpc_samr` and compile a small SAMR client stub user including generated SAMR headers and linking with emitted flags.
