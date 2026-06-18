# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zsysvm.c

## Purpose
Implements non-standard Ghostscript operators for allocating arrays, dictionaries, packed arrays, and strings in explicit VM spaces: local, global, or system.

## Public Surface
Registered operators include:
- `.globalvmarray`, `.globalvmdict`, `.globalvmpackedarray`, `.globalvmstring`.
- `.localvmarray`, `.localvmdict`, `.localvmpackedarray`, `.localvmstring`.
- `.systemvmarray`, `.systemvmdict`, `.systemvmpackedarray`, `.systemvmstring`.
- `.systemvmcheck`.

## Implementation Notes
- `specific_vm_op` temporarily changes `icurrent_space`, calls the normal creation operator, then restores the old space.
- Wrappers reuse existing `zarray`, `zdict`, `zpackedarray`, and `zstring`.
- `.systemvmcheck` returns whether an object lives in `avm_system`.

## Dependencies
Uses Ghostscript interpreter allocation space controls from `ialloc.h` and `ivmspace.h`.

## Risks and Notes
- Correct restoration of allocation space is critical after delegated operator failure or success.
- System VM is outside normal save/restore semantics and should only contain simple or system-VM composite references.
- Filesystem relevance: none directly; VM allocation policy only.
