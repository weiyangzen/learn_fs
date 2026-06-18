# File Research: sources/os/bsd/freebsd-src/sys/sys/uuid.h

DCE-compatible UUID structure and generation/parsing interface.

Key responsibilities:
- Defines UUID node length and kernel UUID generation batch maximum.
- Defines `struct uuid` in DCE 1.1 source layout: time fields, clock sequence fields, and 6-byte node.
- Under `_KERNEL`, exposes UUID node length, kernel UUID generation, Ethernet node add/delete, string formatting helpers, sbuf formatting, validation/parsing flags and functions, comparison, and big/little-endian encode/decode helpers.
- In userland, aliases `uuid_t` to `struct uuid` and declares `uuidgen()`.

Dependencies:
- Includes `sys/types.h`; kernel formatting uses `struct sbuf`.

Notable risks:
- `UUIDGEN_BATCH_MAX` limits allocations per call and should be preserved as a resource-safety boundary.
- Validation can check only format or also semantics depending on flags; callers must request the intended strictness.
