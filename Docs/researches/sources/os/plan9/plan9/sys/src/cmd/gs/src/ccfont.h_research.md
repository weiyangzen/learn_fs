# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ccfont.h

This header defines the interface and data helpers for Ghostscript fonts compiled into C.

Key contents:
- Includes core interpreter and memory headers needed by compiled font data.
- Defines typed ref initializer helpers for booleans, integers, nulls, and reals.
- Defines `charindex`, used to map encoding/vector indices.
- Defines `cfont_string_array`, a compact byte-string representation for mostly-string arrays; elements encode string/name length, nulls, or token-scanned strings.
- Defines `cfont_dict_keys`, carrying dictionary construction metadata such as encoding keys, string key count, extra slots, and object protection flags.
- Defines `cfont_procs`, a procedure vector used by generated compiled-font code to create dictionaries, arrays, names, refs, and strings without hard external dependencies.
- Defines `ccfont_proc`, `ccfont_fproc`, `ccfont_fprocs`, and `ccfont_version`.

Design purpose:
- Lets compiled font objects be linked into Ghostscript or third-party shared libraries while exposing only a small procedural interface.
- No filesystem behavior is present; generated C font data is consumed from memory after compilation.
