# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/dict.h

This header defines common dictionary structures, private-use marker runes, and function prototypes for all dictionary backends.

Key contents:
- Private Use Area marker enum for special output actions: `NONE`, tag markers, special character names, paragraph breaks, ligature classes, and multi-rune expansions.
- `Entry` describes an in-memory dictionary entry with `start`, `end`, and dictionary offset `doff`.
- `Assoc` maps string keys to long values.
- `Nassoc` maps numeric keys to long values.
- `Dict` describes a dictionary backend: name, description, data path, index path, `nextoff()`, `printentry()`, and `printkey()`.
- Declares common output/conversion helpers such as `fold()`, `foldre()`, `outprint()`, `outrune()`, `outpiece()`, `liglookup()`, `changett()`, and lookup helpers.
- Declares backend entry points for OED, AHD, movie, Roget, thesaurus, world, slang, simple dictionaries, and others.
- Exposes globals `bdict`, `bout`, `linelen`, `breaklen`, `outinhibit`, `debug`, `multitab`, and `dicts`.

Notable implementation details:
- `Nligs` and `Nmulti` derive table sizes from enum ranges.
- The `Dict` interface is intentionally small: offset navigation, entry printing, and key printing.
