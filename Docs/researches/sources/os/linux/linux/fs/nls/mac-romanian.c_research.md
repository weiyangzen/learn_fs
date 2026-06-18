# File Research: sources/os/linux/linux/fs/nls/mac-romanian.c

Implements the `macromanian` NLS codepage module.

Key behavior:
- Provides generated mappings for Mac Romanian, mostly Mac Roman-compatible with Romanian-specific substitutions.
- Includes Romanian code points such as `0102/0103`, `0218/0219`, and `021a/021b`.
- Reverse lookup uses pages `00`, `01`, `02`, `03`, `20`, `21`, `22`, `25`, and `f8`.
- Conversion callbacks are exact one-byte mappings with `-ENAMETOOLONG` for no output space and `-EINVAL` for unmappable Unicode or invalid decoded bytes.
- Registers charset name `macromanian`.

Important interactions:
- Shares the same Linux NLS module registration path and conversion contract as the other generated Mac codepages.
- Case mapping data is table-supplied, not locale-sensitive logic.
