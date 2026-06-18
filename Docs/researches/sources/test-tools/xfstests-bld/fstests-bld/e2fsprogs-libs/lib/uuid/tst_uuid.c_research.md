# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/tst_uuid.c

Purpose: `tst_uuid.c` is a standalone smoke and regression test program for the UUID library. It validates generation, parsing, unparsing, type/variant decoding, comparison, clearing, copying, and selected invalid parse inputs.

Important APIs, types, and functions: `test_uuid()` wraps `uuid_parse()` expectations for valid or invalid strings. `main()` uses public libuuid APIs from `<uuid/uuid.h>`: `uuid_generate()`, `uuid_generate_random()`, `uuid_generate_time()`, `uuid_unparse()`, `uuid_type()`, `uuid_variant()`, `uuid_time()`, `uuid_parse()`, `uuid_compare()`, `uuid_clear()`, `uuid_is_null()`, and `uuid_copy()`. It conditionally defines GCC unused attributes and has a Windows compatibility include block.

Control flow: `main()` generates a default UUID, prints string and raw bytes, and checks the DCE variant. It repeats for random UUID generation and additionally requires type 4. It then generates a time UUID, requires DCE variant and type 1, decodes its timestamp, parses the printed string back, and compares it with the original. It clears and checks a UUID for nullness, copies and compares another UUID, and finally runs a table of canonical/invalid parse strings through `test_uuid()`. Any failure increments `failed`; nonzero failures exit with status 1.

State and persistence: the program keeps only local stack buffers and an integer failure count. It prints diagnostics to stdout/stderr and returns process status as the persistent test signal. It does not create files.

Dependencies and integration points: depends on the installed or in-tree `<uuid/uuid.h>` and the UUID library implementation. It is a build/test target signal for the libuuid subset and cross-checks implementation files in this group, including `parse.c`, `unparse.c`, `uuid_time.c`, and private pack/unpack behavior.

Risks: generated UUID expectations depend on the generation backend being available and setting correct variant/type bits. The test prints `timeval` fields with `%ld`, which matches many Unix ABIs but can be portability-sensitive. It is a smoke test, not exhaustive property testing; it does not test all variants, null input, buffer sizing, or malformed high-bit characters.

Test signals: the executable's exit code is the primary signal. The parse cases cover uppercase/lowercase acceptance, too-long and too-short strings, misplaced separators, missing separators, and non-hex characters at both ends.
