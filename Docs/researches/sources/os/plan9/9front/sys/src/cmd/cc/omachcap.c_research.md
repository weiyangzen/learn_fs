# File Research: sources/os/plan9/9front/sys/src/cmd/cc/omachcap.c

Default machine-capability hook for compiler back ends.

Key behavior:
- Defines `machcap(Node*)` to always return `0`.
- Comment notes this is the default behavior, like old `cc`.

Dependencies:
- Includes `cc.h`.

Research notes:
- Architecture-specific compiler variants can override this hook.
