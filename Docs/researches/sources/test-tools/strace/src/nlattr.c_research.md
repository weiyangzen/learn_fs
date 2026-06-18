<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.c -->
# sources/test-tools/strace/src/nlattr.c

Purpose: generic netlink attribute iterator and library of reusable typed nla payload decoders.

Important APIs/types/functions: `decode_nlattr`, `decode_nlattr_with_data`, `fetch_nlattr`, `print_nlattr`, scalar `DECL_NLA` decoders, `decode_nla_xval`, `decode_nla_flags`, `decode_nla_af_spec`, and typed helpers for strings, fd, uid/gid, ifindex, hwaddr, inet addresses, byte-order integers, meminfo, protocols, and variable-sized integers.

Control flow: iterates aligned `struct nlattr` records with truncation checks, prints header length/type including `NLA_F_NESTED` and `NLA_F_NET_BYTEORDER`, dispatches payload by type index or no-type decoder mode, and falls back to hex when no decoder succeeds.

State and persistence behavior: no persistent state. It only reads tracee memory and uses caller-provided opaque context for xlat options or nested decoder state.

Dependencies and integration points: used by nearly every netlink family decoder; depends on `netlink.h`, `nlattr.h`, network byte-order helpers, socket diag meminfo xlats, address printers, and `print_ifindex`/`print_hwaddr`.

Risks: invalid `nla_len`, address overflow, zero-size decoder semantics, and opaque-data misuse can produce wrong output. New kernel attribute scalar sizes may need new decoders.

Test signals: nested attributes, short headers, malformed lengths, unknown types, flags, xval with endian conversion, meminfo arrays, hardware addresses, AF_SPEC dispatch, and no-type nested arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.c -->
