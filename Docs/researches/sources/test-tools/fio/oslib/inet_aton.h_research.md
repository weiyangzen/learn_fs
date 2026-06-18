# sources/test-tools/fio/oslib/inet_aton.h

Purpose: declaration for fio's `inet_aton()` fallback.

Important APIs/types: includes `<arpa/inet.h>` and declares `inet_aton(const char *, struct in_addr *)`.

Control flow and state: no logic or state.

Dependencies and integration: paired with `inet_aton.c`; also overlaps with Windows `posix.h` declaration.

Risks: duplicate declarations must agree with platform headers and configuration. This header should only be used when the fallback is needed or harmless.

Test signals: compile matrix with native and fallback `inet_aton()`.
