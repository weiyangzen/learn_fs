# sources/user-network-fs/impacket/tests/misc/test_utils.py

Purpose: Tests example-script credential and target parsing helpers.

Important APIs, types, and functions: Uses `parse_target` and `parse_credentials` from `impacket.examples.utils`.

Control flow: Each test defines a dictionary of input strings to expected tuples and loops through them with `assertTupleEqual`. `parse_target` cases include host-only, username, password, domain, slashes, colons, and passwords containing `@`. `parse_credentials` cases cover domain, username, password, extra colons, and slash-containing passwords.

State and persistence behavior: Pure string parsing; no external state.

Dependencies and integration points: These helpers are widely used by Impacket example CLI tools for interpreting user-supplied targets and credentials.

Risks: Ambiguous delimiters in passwords are common user-facing edge cases. The tests intentionally preserve `@`, `:`, and `/` inside password fields where appropriate.

Test signals: Good signal for parsing empty inputs, domain/user separators, target host extraction, password delimiter handling, and credential-only parsing.
