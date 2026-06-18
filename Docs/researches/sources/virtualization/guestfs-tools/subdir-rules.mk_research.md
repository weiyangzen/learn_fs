# File Research: sources/virtualization/guestfs-tools/subdir-rules.mk

Shared Automake include for guestfs-tools subdirectories.

Key behavior:
- Includes top-level `common-rules.mk`.
- Defines generator dependencies through `generator_built` and `generator/stamp-generator`.
- Sets `LOG_DRIVER` to the guestfs test driver.
- Defines OCaml build mode variables based on `HAVE_OCAMLOPT`: bytecode/native archive suffix, `BEST`, and custom-link flags.
- Defines silent-rule variables for OCaml, Java, Erlang, POD, jar, and po4a translation actions.
- Provides pattern rules for `.mli -> .cmi`, `.ml -> .cmo`, and, when native compilation is available, `.ml -> .cmx`.

Research notes:
- Many `Makefile.am` files in this batch rely on these OCaml compilation and generated-code rules.
