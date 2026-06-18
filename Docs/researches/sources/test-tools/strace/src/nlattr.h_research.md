<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.h -->
# sources/test-tools/strace/src/nlattr.h

Purpose: public interface for netlink attribute decoding and typed nla decoder declarations.

Important APIs/types/functions: `struct decode_nla_xlat_opts`, `struct ifla_linkinfo_ctx`, `nla_decoder_t`, `decode_nlattr`, `decode_nlattr_notype`, `DECL_NLA`, typed decoder declarations, `decode_nla_hwaddr_family`, `decode_nla_hwaddr_nofamily`, `struct af_spec_decoder_desc`, and `decode_nla_af_spec`.

Control flow: inline wrappers adapt `decode_nlattr` for special no-type and hardware-address cases; most behavior is implemented in `nlattr.c`.

State and persistence behavior: declares context structures but owns no state. `ifla_linkinfo_ctx` is caller-managed state for linkinfo decoding.

Dependencies and integration points: includes `xlat.h` and is consumed by route, sock_diag, generic, crypto, netfilter, and other netlink decoders.

Risks: the zero-size decoder convention passes `nla_type` through `opaque_data`, so callers must not also expect opaque context in that mode. Hardware family encoding uses `NLA_HWADDR_FAMILY_OFFSET` sentinel bits.

Test signals: compile all declared decoders, no-type nested decoding, AF_SPEC selection, hardware address family wrappers, and xlat option scalar/flags decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/nlattr.h -->
