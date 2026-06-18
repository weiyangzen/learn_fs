# sources/test-tools/fio/lib/bloom.c

Purpose: implements a Bloom filter with five hash functions for approximate duplicate detection over word arrays or strings.

Important APIs/functions: `bloom_new`, `bloom_free`, `bloom_set`, and `bloom_string`. Static hash wrappers bind Jenkins, XXH32, murmur3, crc32c, and FNV to a shared seed; `__bloom_check` computes indexes, checks all bits, and optionally sets missing bits.

Control flow: construction probes crc32c acceleration, allocates the filter and a zeroed `uint32_t` map sized by entry count. A check hashes the input five times, mods by `nentries`, and tests or sets the corresponding bit positions.

State/persistence: heap-owned filter with `nentries` and mutable bit map. It is probabilistic and in-memory only.

Dependencies/integration: depends on fio hash and crc libraries, `types.h`, and platform crc probes. It can be used by verify/dedupe-style flows that need compact seen-set behavior.

Risks/test signals: `bloom_new` does not check allocation of `struct bloom` before assigning `nentries`; zero `entries` would also make modulo invalid. False positives are expected. Tests should cover allocation failure assumptions, repeated insert returning already-seen, non-setting lookup, and string length handling.
