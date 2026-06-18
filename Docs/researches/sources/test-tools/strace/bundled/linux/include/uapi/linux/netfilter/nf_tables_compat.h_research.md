# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nf_tables_compat.h

Purpose: defines nftables compatibility ABI for translating/querying legacy xtables matches and targets through nfnetlink.

Important APIs/types/functions: exports target attributes (`NFTA_TARGET_NAME`, `REV`, `INFO`), match attributes (`NFTA_MATCH_NAME`, `REV`, `INFO`), `NFT_COMPAT_NAME_MAX`, `NFNL_MSG_COMPAT_GET`, and compat query attributes (`NFTA_COMPAT_NAME`, `REV`, `TYPE`).

Control flow: userspace asks the nf_tables compat subsystem about legacy match/target support and embeds match/target info blobs inside nftables compatibility expressions/rules.

State/persistence behavior: query messages are observational. When used in nft rules, the info blobs become persistent ruleset state managed through the main nf_tables ABI.

Dependencies/integration: integrates with nfnetlink subsystem `NFNL_SUBSYS_NFT_COMPAT`, xtables modules, and `nf_tables.h` rule compatibility attributes.

Risks and test signals: `INFO` is opaque module-specific binary data. Tests should decode match/target names, revisions, compat type, name-length limits, and nested use from nft rule expressions without assuming blob structure.
