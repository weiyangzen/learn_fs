# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_prop.c

Read completely: 467 lines.

This implements the Citrus module property-string parser. It parses named properties according to a caller-provided hint table, supports booleans, strings, characters, and unsigned numeric ranges, and invokes type-specific callbacks for parsed values.

Key pieces: `_citrus_prop_object_t` stores the temporary value; generated integer readers handle decimal/octal/hex with cutoff checks; `_citrus_prop_read_character_common` supports C-style escapes; `_citrus_prop_read_str` supports quoted and unquoted strings; `_citrus_prop_parse_element` matches a symbol against hints and handles comma-separated value/range lists; `_citrus_prop_parse_variable` drives the whole stream.

Important interactions: BIG5 and HZ use this parser for runtime encoding variables; additional Citrus modules can define their own hint tables. It depends on `_memstream` and BCS classification rather than libc locale-sensitive parsing.

Security/reliability notes: numeric readers avoid accumulator overflow by cutoff/cutlim checks. String allocation grows in fixed chunks. The parser rejects unknown property names and malformed separators. Since callbacks receive parsed data directly and may allocate nested structures, callback failure paths are important to audit in the module using the parser.
