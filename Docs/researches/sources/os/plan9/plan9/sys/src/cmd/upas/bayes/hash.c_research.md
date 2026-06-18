# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/hash.c

- Role: String-count hash table implementation and serialized hash table I/O for Bayes tools.
- Key functions: `findstab`, `sortstab`, `Bwritehash`, `Breadhash`, `freehash`, `Bopenlock`.
- Memory model: Allocates `Stringtab` entries in large pools and string bytes in 512 KiB chunks; free list recycles entries.
- Format: `# hash table` header followed by `token<TAB>count date`; writes skip nonpositive and older-than-30-day entries.
- Risks/notes: `freehash` frees the `Hash` pointer itself, so callers must allocate hashes dynamically unless they avoid freeing.
