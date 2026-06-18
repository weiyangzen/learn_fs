# File Research: sources/os/plan9/9front/sys/src/cmd/upas/ml/dat.h

Header for mailing-list utilities.

Key contents:
- Includes SMTP/RFC822 parser headers.
- Defines linked-list `Addr`.
- Declares shared globals: `from`, `sender`, `firstfield`, `naddrlist`, `addrlist`.
- Declares shared helper functions from `common.c`.

Filesystem relevance:
- Supports the list tools that read/write address-list files and invoke upas delivery.

Notable constraints:
- Depends on parser types `Field`, `Node`, and token constants from `../smtp/rfc822.tab.h`.
