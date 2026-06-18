# sources/sync-backup/bup/lib/bup/cmd/validate_ref_links.py

## Purpose
`validate_ref_links.py` is a compatibility wrapper that runs `validate_refs` in link-validation mode.

## APIs and Control Flow
`main(argv)` parses only verbosity and optional refs, constructs a new argv beginning with the original program name, repeats `-v`, appends `--links`, appends byte refs, and returns `validate_refs.main(args)`.

## State, Dependencies, Integration, Risks, Tests
It is read-only apart from validation output. Dependencies are `bup.cmd.validate_refs`, option parsing, and `argv_bytes`. It exists to expose a narrower command name/API for missing-link checks. Risks are wrapper drift if `validate_refs` changes option names or if verbosity semantics differ. Test signals include argument forwarding, multiple `-v` preservation, byte ref conversion, and return-code propagation from `validate_refs`.
