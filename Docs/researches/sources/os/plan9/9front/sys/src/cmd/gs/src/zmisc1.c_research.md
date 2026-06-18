# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zmisc1.c

## Purpose
Implements Type 1 font encryption/decryption helpers and eexec filters.

## Key Functions
- `ztype1encrypt()` and `ztype1decrypt()` call shared `type1crypt()`.
- `type1crypt()` encrypts/decrypts a source string into a target string and returns the updated state.
- `eexec_param()` parses eexec seed operands.
- `zexE()` creates `eexecEncode`.
- `zexD()` creates `eexecDecode`.

## Important Behavior
- Type 1 crypt state is range-checked against truncation to `crypt_state`.
- Output string must be at least as large as input.
- eexec decode supports dictionary parameters `seed`, `lenIV`, and `eexec`.
- If decoding a PFB stream, the filter captures PFB state and can avoid binary-to-hex roundtripping.

## Research Notes
Font/filter-specific interpreter glue around stream templates and Type 1 crypto helpers.
