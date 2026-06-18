# File Research: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.h

- Purpose: public hash API and convenience macros.
- Key APIs: `hash`, `hash_stable`, `hash_u32`, `hash_string`, `hash64`, `hash64_stable`, `hashl`, `hash_pointer`, and underlying function declarations.
- Type policy: stable hash macros assert element sizes of 1, 2, 4, or 8 bytes.
- Pointer hashing: safely aliases pointer representation through a union when possible.
