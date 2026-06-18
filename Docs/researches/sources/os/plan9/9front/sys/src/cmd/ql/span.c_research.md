# File Research: sources/os/plan9/9front/sys/src/cmd/ql/span.c

This file computes final instruction addresses, classifies operands, selects optab rows, handles long conditional branches, and emits dynamic relocation tables.

Key responsibilities:
- `span()` assigns PCs starting at `INITTEXT`, handles `TEXT` origin overrides, updates text symbol values, expands out-of-range conditional branches into longer branch sequences, aligns text, sets `textsize`, and derives `INITDAT` from `INITRND`.
- `aclass()` classifies `Adr` operands into `C_*` classes and computes `instoffset`.
- `regoff()` returns the offset computed by `aclass()`.
- `oplook()` selects and caches the matching `Optab` entry for a `Prog`.
- `cmp()` defines class compatibility rules used by `buildop()`.
- `buildop()` sorts `optab`, builds opcode ranges, and aliases opcode families to shared table ranges.
- `dynreloc()` records dynamic relocations in sorted address order.
- `asmdyn()` serializes import names/signatures and compressed relocation records.

Important behavior:
- In dynamic-linking mode, external/static operands become `C_ADDR` or large constants and relocation records are attached later during encoding/data emission.
- Conditional branches that exceed signed 16-bit reach are rewritten with inverted/extra branches and inserted no-ops.
- `buildop()` is tightly coupled to `optab.c` and must run before instruction lookup.

Implementation notes:
- The file intentionally defines `r0iszero` as `1` locally for operand classification decisions.
- Relocation records encode absolute/relative, defined/undefined, split, and sign-extension modes through compact mode values.
