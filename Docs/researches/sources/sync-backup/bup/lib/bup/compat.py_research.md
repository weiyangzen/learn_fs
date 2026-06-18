# sources/sync-backup/bup/lib/bup/compat.py

## Purpose
`compat.py` centralizes Python-version compatibility and process argv byte handling for bup.

## APIs and Control Flow
It exports `environ`, `fsencode`, `pairwise` for Python < 3.10, `print_exception` with 3.10-style calling on older versions, `argv_bytes`, `get_argvb`, `get_argv`, `dataclass`, and `dataclass_frozen_for_testing`. `argv_bytes` uses `os.fsencode`; `get_argvb` and `get_argv` read original bytes from `bup_main.argv`. The dataclass wrapper drops `slots` on older Python, and the testing variant only freezes when `BUP_TEST_LEVEL` is set.

## State, Dependencies, Integration, Risks, Tests
State depends on Python version and environment. Dependencies include `bup_main`, `dataclasses`, and `traceback`. This module is imported broadly by command parsers and typed data structures to preserve byte argv semantics. Risks include losing slots behavior on older Python, `dataclass_frozen_for_testing` changing mutability only under tests, surrogateescape decode assumptions, and compatibility wrappers falling behind Python APIs. Test signals include pairwise fallback, print_exception compatibility, original argv byte preservation, dataclass slots/frozen behavior across env settings, and `get_argv` decoding.
