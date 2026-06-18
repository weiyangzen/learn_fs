# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/mac.c

This file includes the shared compiler header and the generated/included macro preprocessor body.

Key behavior:
- Includes `cc.h`.
- Includes `macbody`, which supplies macro/preprocessor implementation used by the lexer.

Important details:
- The file itself is only an inclusion wrapper; behavior lives in `macbody`.

Filesystem relevance:
- Indirect compiler support.
