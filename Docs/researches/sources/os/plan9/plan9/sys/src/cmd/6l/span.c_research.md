# File Research: sources/os/plan9/plan9/sys/src/cmd/6l/span.c

## Purpose
Performs instruction sizing, address assignment, symbol emission, line table emission, x86-64 instruction encoding, and dynamic relocation table generation for `6l`.

## Key Functions
- `span()` iteratively assigns PCs and resizes branch encodings until stable.
- `xdefine()`, `putsymb()`, `asmsym()`, and `asmlc()` emit linker symbols and line-number tables.
- `oclass()` classifies operands into `Y*` classes used by `optab.c`.
- `asmidx()`, `asmandsz()`, `asmand()`, and `asmando()` encode ModR/M, SIB, displacement, and register addressing.
- `vaddr()`, `put4()`, and `put8()` compute absolute values and generate dynamic relocations when needed.
- `doasm()` interprets `Optab` entries and emits machine bytes for each `Z*` encoding form.
- `asmins()` inserts REX prefixes at the correct byte position.
- `dynreloc()` and `asmdyn()` collect and emit dynamic relocation/import records.

## Important Behavior
- Branch sizing is iterative because short vs long conditional jumps affect downstream PCs.
- `AADJSP` pseudo-instructions are rewritten into `ADD/SUB SP` before sizing.
- Address classification rejects 64-bit-only registers outside 64-bit mode and distinguishes immediates by signed/unsigned width.
- Special `ymovtab` handles segment/control/debug/task descriptor moves and other irregular x86 instructions.
- REX prefix placement is carefully adjusted after legacy prefixes.

## Research Notes
This is the executable encoder. It consumes `optab.c`’s declarative table and produces bytes, relocation records, symbols, and line metadata.
