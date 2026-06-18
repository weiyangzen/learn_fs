# File Research: sources/virtualization/nvme-cli/libnvme/test/uuid.c

This file tests libnvme UUID formatting, parsing, and random UUID generation.

Coverage:
- `test_data[]` maps raw 16-byte UUID values to canonical lowercase string forms.
- `tostr_test()` calls `libnvme_uuid_to_string()` and compares against expected strings.
- `fromstr_test()` calls `libnvme_uuid_from_string()` and compares raw bytes.
- `random_uuid_test()` calls `libnvme_random_uuid()` twice, checks the values differ, converts both to strings, and prints them.

Helpers:
- `check_str()` reports string mismatches and sets global `test_rc`.
- `check_uuid()` reports byte mismatches in hex. It does not set `test_rc`, which looks like a minor test bug: a parse mismatch would print an error but not fail unless another error set `test_rc`.

Integration:
- Uses `NVME_UUID_LEN` and `NVME_UUID_LEN_STRING` from libnvme.
- Meson registers it as `libnvme - uuid`.

Risk and maintenance notes:
- Randomness equality check is probabilistic but practically safe for UUID-sized values.
- `check_uuid()` should set `test_rc = 1` on mismatch for strict failure semantics.
