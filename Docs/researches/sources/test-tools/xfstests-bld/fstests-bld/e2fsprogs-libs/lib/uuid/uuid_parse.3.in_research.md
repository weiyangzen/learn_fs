# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_parse.3.in

Purpose: manpage template for `uuid_parse()`, documenting conversion from canonical UUID text to binary representation.

Important APIs, types, and functions: documents `int uuid_parse(char *in, uuid_t uu)`, returning 0 on success and -1 on parse failure. The implementation has `const char *in`, so the documentation is slightly less const-correct.

Control flow: documentation only. It describes the accepted format as 36 bytes plus trailing NUL with hyphenated hex groups.

State and persistence: installed documentation. The described function writes the parsed UUID into caller-provided memory and otherwise has no persistence.

Dependencies and integration points: must match `parse.c`, `uuid.h.in`, and `uuid_unparse.3.in`. It cross-references generation, time, and unparse APIs.

Risks: the manpage's format string `%08x-%04x-%04x-%04x-%012x` is a conceptual description; the implementation actually parses the node as six byte pairs. If accepted forms ever expand beyond canonical hyphenated strings, this page must change.

Test signals: `tst_uuid.c` parse-valid and parse-invalid cases directly validate the documented behavior. Manpage substitution fills e2fsprogs date/version.
