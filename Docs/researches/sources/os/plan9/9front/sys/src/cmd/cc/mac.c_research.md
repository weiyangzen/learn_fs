# File Research: sources/os/plan9/9front/sys/src/cmd/cc/mac.c

Tiny compilation unit that includes shared macro-processing implementation.

Key behavior:
- Includes `cc.h`.
- Includes `"macbody"`, which supplies the actual macro/preprocessor helper code for this compiler build.

Dependencies:
- Depends entirely on `cc.h` and the local `macbody` include file.

Research notes:
- This file is a wrapper, not an implementation body itself.
