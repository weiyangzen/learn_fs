# File Research: sources/virtualization/nvme-cli/ccan/ccan/hash/hash.c

- Purpose: Bob Jenkins lookup3-derived hash implementation for CCAN.
- Key implementations: `hash_u32`, endian-selecting byte hash via `hashlittle`/`hashbig`, stable 64/32/16/8-bit element hashing, `hash_any`, and `hash64_any`.
- Endian behavior: internal hashes may differ by machine; stable hashes process integer elements to preserve cross-endian results.
- Collision domain: intended for hash table lookup, explicitly not cryptographic.
- Notes: disabled `SELF_TEST` block contains upstream test code with older function names; normal nvme-cli build compiles the production functions.
