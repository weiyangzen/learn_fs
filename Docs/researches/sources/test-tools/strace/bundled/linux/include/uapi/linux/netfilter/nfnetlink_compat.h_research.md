# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_compat.h

Purpose: provides legacy nfnetlink attribute helpers and old multicast group bitmasks for userspace compatibility.

Important APIs/types/functions: declares `struct nfattr`, old group masks such as `NF_NETLINK_CONNTRACK_NEW`, nesting/type macros `NFNL_NFA_NEST`, `NFA_TYPE`, alignment and traversal macros `NFA_ALIGN`, `NFA_OK`, `NFA_NEXT`, `NFA_LENGTH`, `NFA_SPACE`, `NFA_DATA`, `NFA_PAYLOAD`, and message helpers `NFM_NFA`/`NFM_PAYLOAD`.

Control flow: legacy parsers walk `nfattr` TLVs using length/alignment macros and detect nested payloads with the high type bit. Kernel-side helper macros are present for historical source compatibility.

State/persistence behavior: no runtime state; it defines binary parsing/wrapping rules for older nfnetlink payloads.

Dependencies/integration: depends on Linux types and assumes netlink/nfgenmsg helpers from including contexts. It is included by `nfnetlink.h`.

Risks and test signals: this header contains kernel-oriented statement macros that userspace tracers should not execute. Tests should validate alignment math, nested type masking, old group bit decoding, and payload length formatting.
