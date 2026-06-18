# File Research: sources/os/bsd/netbsd-src/lib/libc/include/namespace.h

Central libc namespace-protection header.

Purpose:
- Remaps public libc function/data names to internal underscored symbols so libc-internal calls cannot be interposed by application symbols.
- Under `__weak_alias`, implementations define the underscored symbol and expose the public name via weak alias.
- Includes broad coverage across hash, stdio, networking, resolver, RPC, pthread-adjacent wrappers, syscalls, locale, time, inet, iconv, dynamic loading, rb trees, and more.

Relevant to this group:
- Remaps hash APIs (`MD2*`, `RMD160*`, `SHA1*`, `SHA2*`, `SHA3*`).
- Remaps `iconv`, `iconv_open`, `iconv_close`.
- Remaps inet APIs such as `inet_ntop`, `inet_pton`, `inet_net_pton`, `inet_cidr_ntop`.
- Remaps `sysctl`, syscall wrappers, RPC locks, and resolver functions.

Also includes a project-specific `__learn_tree` remap to `___learn_tree`.
