# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fixarenas.c

Implements `fixarenas`, a forensic arena-partition checker and repair tool designed to keep recovering usable clumps despite local corruption. Unlike `checkarenas`, it can infer geometry, scan raw data, rewrite metadata, zero corrupt spans, rebuild clump directories, and reseal arenas.

It first guesses arena geometry from intact arena heads/tails when needed, including arena size, block size, arena base, table base, and table size. It validates or rewrites the arena partition superblock and can check selected ranges.

The repair path uses paged read/write buffers, robust fallback reads down to 512-byte sectors, and SHA1 streaming buffers with rollback checkpoints for resealing. `isclump()` recognizes candidate clumps by magic, type, sizes, encoding, decompression, and score verification.

`guessarena()` reconstructs one arena: it loads basic name/version/magic hints from head/tail, scans clump payloads, tracks corrupt regions as synthetic `VtCorruptType` directory entries, computes stats and timestamps, adjusts directory space, rewrites clump-info blocks, optionally zeros bad data, unseals if there is large unused space, and computes new seal scores when fixing.

`checkarena()` compares reconstructed headers and tails against disk bytes with field-aware diff output, writes corrected bytes in `-f` mode, and can dump repaired arena images with `-x`. `checkmap()` rebuilds the arena partition map from recovered arena heads and rewrites it if different.

Important options include `-f` for write repair, `-U` to unseal, `-a`/`-b` to override arena/block size guesses, `-n` for base arena name, `-v` for detail, and optional arena ranges.
