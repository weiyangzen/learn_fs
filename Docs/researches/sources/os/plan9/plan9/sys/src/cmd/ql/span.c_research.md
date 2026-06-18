# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/span.c

PC assignment, operand classification, opcode lookup, branch relaxation, and dynamic relocation emission.

Key functions:
- `span()` assigns PCs from `INITTEXT`, uses `oplook()` sizes, handles `TEXT` origin overrides, detects very large procedures, inserts long-branch workaround sequences when short branches exceed range, aligns text, sets `etext`, `textsize`, and `INITDAT`.
- `xdefine()` defines unresolved symbols if still undefined.
- `aclass()` maps `Adr` operands to linker operand classes and computes `instoffset`.
- `regoff()` returns the offset computed by `aclass()`.
- `oplook()` caches operand classes on `Prog` operands, scans the opcode range for compatible `Optab`, and diagnoses illegal combinations.
- `cmp()` defines class compatibility, allowing narrower classes to satisfy broader table entries.
- `ocmp()` and `buildop()` sort `optab`, build `oprange`, and alias many related opcodes to shared encoding ranges.
- `dynreloc()` records sorted dynamic relocation entries, distinguishing absolute/relative, defined/undefined, split, and sign-extended modes.
- `asmdyn()` emits import names/signatures and compressed relocation deltas.

Risk/notes:
- `#define r0iszero 1` makes zero-register behavior fixed within this file.
- `aclass()` is where dynamic-module addressing diverges from normal static linking.
- Branch relaxation mutates the instruction stream after an initial span pass.
