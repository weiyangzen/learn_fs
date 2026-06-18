# File Research: sources/os/plan9/9front/sys/src/cmd/7l/asm.c

ARM64 linker output writer. It emits final machine code bytes, data segments, symbol tables, line tables, dynamic module records, and Plan 9 executable headers.

Key functions:
- `entryvalue` resolves the executable entry point from `INITENTRY`, symbols, or defaults.
- `asmb` is the main output pass: emits text instructions via `asmout`, pads string/data segments, writes initialized data, emits symbols/line tables/dynamic records, and writes the final header.
- `cflush`, `cput`, `wput`, `wputl`, `lput`, `lputl`, `llput`, and `llputl` buffer output and handle endian-specific integer writes.
- `asmsym` emits global, data, bss, string, file, function, frame, auto, and parameter symbols.
- `putsymb` writes one Plan 9 symbol record and updates `symsize`.
- `asmlc` emits compressed line number/PC deltas.
- `datfill` applies `ADATA`/`AINIT`/`ADYNT` records into text-string or data buffers, detects duplicate initialization, applies relocations, and serializes constants/floats/strings.
- `chipfloat` recognizes ARM64 encodable floating immediates.

Important details:
- Supports Plan 9 header type `2`, no-header modes `0`/`6`, and DLM-specific behavior.
- Uses `PADDR` to mask entry address in the 32-bit header field while also writing a full 64-bit entry.
- Handles dynamically loadable modules with `dynreloc` and `asmdyn`.

Filesystem relevance: indirect build/link infrastructure.
