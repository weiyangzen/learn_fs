# sources/test-tools/fio/oslib/inet_aton.c

Purpose: fallback `inet_aton()` implementation.

Important APIs/functions: `inet_aton(const char *cp, struct in_addr *inp)` delegates to `inet_pton(AF_INET, cp, inp)`.

Control flow and state: no state; direct conversion wrapper returning the `inet_pton()` result.

Dependencies and integration: includes `inet_aton.h`, which pulls in `<arpa/inet.h>`. Supports platforms where `inet_aton()` is missing but `inet_pton()` exists.

Risks: historical `inet_aton()` accepted some shorthand IPv4 forms that `inet_pton()` rejects. The return value is compatible for success/failure, but accepted syntax may differ.

Test signals: IPv4 literal parsing, invalid address rejection, and compatibility expectations for shorthand addresses.
