# File Research: sources/virtualization/nvme-cli/unit/test-suffix-si-parse.c

C unit test for SI suffix parsing.

Cases:
- Plain numbers and decimal SI suffixes like `M`, `k`, `T`, and `G`.
- Fractional values are truncated to integer byte/count values.
- Invalid inputs include unsupported characters, comma decimal separator, double dots, repeated suffixes, suffix followed by digits, and trailing decimal point forms.
- Sets numeric locale to `C`.

Role:
- Guards decimal suffix parsing behavior for CLI numeric arguments.
