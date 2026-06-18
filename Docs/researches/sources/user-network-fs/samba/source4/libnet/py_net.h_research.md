# sources/user-network-fs/samba/source4/libnet/py_net.h

## Purpose

`py_net.h` declares the C struct backing the Python `samba.net.Net` object.

## Important APIs, Types, and Functions

`py_net_Object` embeds `PyObject_HEAD` plus `TALLOC_CTX *mem_ctx`, `struct libnet_context *libnet_ctx`, and `struct tevent_context *ev`.

## Control Flow

The constructor in `py_net.c` initializes these fields; the destructor frees `libnet_ctx` before `mem_ctx`.

## State and Persistence Behavior

This object owns the Python-visible libnet session state. Its `libnet_context` may cache RPC pipes and domain handles, and its talloc context owns allocations that should live for the Python object.

## Dependencies and Integration Points

The header is included by `py_net.c` and `py_net_dckeytab.c`, allowing the latter to add a method that can access the underlying `libnet_context`.

## Risks and Edge Cases

Any change to this struct affects binary compatibility between compiled extension modules that include it. Destruction order matters because `libnet_ctx` may reference objects under `mem_ctx`.

## Test Signals

Python extension import, object construction/destruction under leak checkers, and dckeytab method injection validate this contract.
