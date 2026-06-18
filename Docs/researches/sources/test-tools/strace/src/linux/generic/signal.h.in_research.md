# sources/test-tools/strace/src/linux/generic/signal.h.in

Purpose: build-time wrapper template that makes strace include libc `<signal.h>` instead of the kernel `<linux/signal.h>` where those headers conflict.

Important APIs/types/functions: exports no functions; the key contract is the forced `#include <signal.h>` used by generated include paths.

Control flow: there is no runtime flow. During the build, this template becomes an overriding header so later strace source includes see the libc-compatible signal definitions.

State/persistence behavior: build-time include indirection only; no runtime state is read or persisted.

Dependencies/integration: integrates with the generated include directory order and all signal, sigset, and signal-frame decoders that need libc signal types without kernel header conflicts.

Risks/test signals: wrong include precedence can reintroduce `<linux/signal.h>`/libc type clashes; test by regenerating headers and compiling signal decoders on libc/kernel header combinations known to conflict.

Source-read signal: reviewed complete local file (5 lines).
