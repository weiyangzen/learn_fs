# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/parse.c

Purpose: `parse.c` implements `uuid_parse()`, the public conversion from canonical UUID text into the 16-byte `uuid_t` representation.

Important APIs, types, and functions: `int uuid_parse(const char *in, uuid_t uu)` returns `0` on success and `-1` on invalid input. It uses `strlen()`, `isxdigit()`, `strtoul()`, and the private `uuid_pack()` helper. The intermediate representation is `struct uuid` from `uuidP.h`.

Control flow: the function first requires `strlen(in) == 36`. It then scans positions 0 through 36, requiring hyphens at offsets 8, 13, 18, and 23, a terminating NUL at offset 36, and hexadecimal digits everywhere else. After validation, it parses the five UUID text fields with `strtoul()`: 8 hex digits for `time_low`, 4 for `time_mid`, 4 for `time_hi_and_version`, 4 for `clock_seq`, and six two-digit octets for `node`. Finally it calls `uuid_pack()` to write the public 16-byte output.

State and persistence: no persistent state, allocation, or I/O. The only side effect is filling the caller's `uuid_t` on success. On invalid input, the function returns before writing a parsed UUID.

Dependencies and integration points: declared in `uuid.h.in` and documented in `uuid_parse.3.in`. It is used by `tst_uuid.c` and by the debug path in `uuid_time.c`. Its binary output must match `uuid_unparse()` formatting and `uuid_compare()` semantics.

Risks: `strlen(in)` assumes `in` is a valid NUL-terminated string; passing null or unterminated memory is unsafe. The validation loop relies on `isxdigit(*cp)` without casting to `unsigned char`, which is conventional in older C but can be undefined for negative signed-char values outside ASCII. The parser accepts upper and lower case hex but only the canonical hyphenated length and positions. The loop includes `i <= 36` and handles the terminator explicitly; this is intentional but brittle if modified.

Test signals: `tst_uuid.c` includes positive lower/upper-case UUID parse cases and invalid cases for length, misplaced hyphens, and non-hex characters. Round-tripping parsed UUIDs through `uuid_compare()` is the key integration test.
