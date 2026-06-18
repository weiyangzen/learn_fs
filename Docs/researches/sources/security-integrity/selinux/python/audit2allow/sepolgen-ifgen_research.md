<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen -->
# sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen

## Purpose
Parses reference-policy interface headers and optional policy attribute access into an interface-info file used by sepolgen/audit2allow.

## Important APIs, Types, And Functions
Functions are `parse_options()`, `get_attrs()`, and `main()`. It uses `sepolgen.refparser.parse_headers`, `sepolgen.defaults`, `sepolgen.interfaces.InterfaceSet`/`AttributeSet`, `tempfile.NamedTemporaryFile`, and an external `sepolgen-ifgen-attr-helper`.

## Control Flow
`main()` parses output path, header directory, policy path, verbosity/debug, helper path, and `--no_attrs`. It opens the output early, optionally calls the helper to write attribute info to a temporary file and parses it into an `AttributeSet`, parses header files, adds parsed headers plus attributes into an `InterfaceSet`, writes the interface-info file, and returns success only if the reference parser reports success.

## State And Persistence
It writes the selected interface-info output file and uses a temporary file for helper output. It reads policy and header inputs.

## Dependencies And Integration Points
This script connects Python sepolgen parsing with the C helper that reads binary policy access vectors for attributes.

## Risks And Edge Cases
Opening the output before parsing can truncate an existing file even if later parsing fails. Helper execution failures abort. `--no_attrs` trades completeness for independence from binary policy/helper availability.

## Test Signals
Run with fixture headers and `test_dummy_policy`, alternate helper path, `--no_attrs`, verbose/debug parsing, unwritable output, and malformed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/python/audit2allow/sepolgen-ifgen -->
