# File Research: sources/virtualization/nvme-cli/unit/test-suffix-binary-parse.c

C unit test for binary suffix parsing.

Cases:
- Plain integer `1234`.
- Binary suffixes such as `1Ki` and `34Gi`.
- Invalid fractional binary suffix `34.9Ki`.
- Invalid repeated suffix `32Gii`.

Role:
- Verifies `suffix_binary_parse` returns expected values and `-EINVAL` on malformed input.
