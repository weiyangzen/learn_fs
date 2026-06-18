# sources/test-tools/syzkaller/pkg/email/parser_test.go

Purpose: `parser_test.go` is broad regression coverage for email parsing, command extraction, address context handling, bug ID extraction, MIME decoding, links, subjects, and base commit hints.

Important tests: `TestExtractCommand` verifies command syntax variations, CRLF parity, wrapped `test:` arguments, first-command iteration, and set/unset/reject commands. Address tests cover plus-context add/remove and canonicalization. `TestParse` runs many raw message fixtures covering Google Groups footers, own-email detection, multipart/base64 patch attachments, quoted-printable bodies, mailing-list sender/original-from behavior, bug IDs in headers/body/domain links, multi-command extraction, RFC 2047 subject decoding, and strict `base-commit` parsing. `TestDirectlyAddressedTo` checks raw-header context matching.

Control flow and state: tests compare full `Email` structs for exact output. Each parse fixture is also rerun with LF converted to CRLF, with expected body adjusted.

Dependencies and integration: fixtures exercise `ParsePatch`, MIME decoding, command parsing, email list merging, and direct-address logic.

Risks/test gaps: coverage is strong but not exhaustive for malformed MIME nesting, empty own email/domain inputs, or extremely large messages. Full-struct comparisons make intentional output changes noisy but effective at catching regressions.
