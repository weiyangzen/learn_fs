# File Research: sources/virtualization/nbdkit/filters/evil/evil.c

Purpose: corrupts read data to simulate bit flips or stuck bits/wires.

Key details:
- Modes are `cosmic-rays`, `stuck-bits`, and `stuck-wires`.
- Configures corruption probability, stuck probability, and random seed.
- Default probabilities depend on mode.
- Chooses an adaptive power-of-two block size so expected corrupt bits per block is about 100.
- `cosmic-rays` uses a global random state and tightens thread model to serialized requests.
- `stuck-bits` seeds random state by disk offset block so the same backing offsets corrupt consistently.
- `stuck-wires` seeds only by global seed so the same positions within every request corrupt consistently.
- Probabilities near zero skip corruption; probabilities above `1/8` corrupt all bits.
- `.pread` delegates to backend then corrupts the returned buffer.

Integration notes:
- This is test/fault-injection code, not a storage transform preserving data integrity.
