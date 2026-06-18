# File Research: sources/virtualization/guestfs-tools/builder/index-parser-c.c

## Scope

C/OCaml bridge for the flex/bison virt-builder index parser.

## Behavior

- Exposes `virt_builder_parse_index` to OCaml.
- Initializes `parse_context` with program name, input filename, and error suffix.
- Opens the index file, runs `do_parse`, converts parse errors into OCaml invalid-argument exceptions, and maps close errors to Unix exceptions.
- Converts linked C sections into OCaml arrays of `(section_name, fields)` tuples.
- Converts each field into `(key, subkey option, value)`.
- Frees the C parse tree after conversion.

## Dependencies And Risks

- Uses OCaml runtime allocation macros and must keep values rooted through `CAMLparam`/`CAMLlocal`.
- Assumes parser output remains valid until copied into OCaml strings.
- File I/O failures surface through OCaml Unix exceptions.
