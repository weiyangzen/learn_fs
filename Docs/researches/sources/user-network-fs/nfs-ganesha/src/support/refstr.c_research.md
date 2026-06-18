# sources/user-network-fs/nfs-ganesha/src/support/refstr.c

## Purpose
This file provides the allocation and final release functions for Ganesha reference-counted strings (`gsh_refstr`). It supports shared immutable-ish strings whose lifetime is controlled by URCU reference counters.

## Important APIs, Types, And Functions
`gsh_refstr_alloc(size_t len)` allocates `sizeof(struct gsh_refstr) + len` bytes and initializes `gr_ref` with `urcu_ref_init`. `gsh_refstr_release(struct urcu_ref *ref)` is the release callback: it recovers the containing `gsh_refstr`, logs the string value, and frees the allocation.

## Control Flow
Allocation returns an initialized container with room for caller-managed string bytes. Release is called when the URCU refcount reaches zero; it uses `container_of` on the embedded reference member and frees the whole object.

## State And Persistence
There is no global state and no persistence. Each allocation owns one heap object and an embedded reference counter. The caller is responsible for filling `gr_val` and ensuring the requested length includes any required terminator.

## Dependencies And Integration Points
The code depends on `gsh_refstr.h`, URCU refs, Ganesha allocation helpers, list/container macros, and export-component logging. It is used by subsystems that need shared strings without copying on every reference.

## Risks And Test Signals
Risks include no explicit allocation failure check before `urcu_ref_init`, caller mistakes around length and null termination, and logging `%s` on `gr_val` assuming it is a valid C string. Tests should cover allocation length including terminator, ref increment/decrement lifecycle, release callback invocation, allocation failure injection, and sanitizer checks for unterminated `gr_val` use.
