# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_hook.h

Purpose: defines nfnetlink hook introspection ABI for listing registered netfilter hooks and associated nftables/BPF/flowtable metadata.

Important APIs/types/functions: exports `NFNL_MSG_HOOK_GET`, hook attributes for hook number, priority, device, function name, module name, and chain info; chain info attributes for description/type; chain description attrs for table/family/name; hook chain types; and BPF attrs for program ID.

Control flow: userspace sends hook get/dump requests and receives records describing hook registrations and their owning module/function or base-chain metadata.

State/persistence behavior: read-only introspection over live hook registrations. Output changes as nftables chains, BPF programs, modules, and flowtables register/unregister hooks.

Dependencies/integration: uses nfnetlink subsystem `NFNL_SUBSYS_HOOK`; chain descriptors depend on `nf_tables.h` table attributes and BPF program IDs.

Risks and test signals: nested chain info changes shape based on type. Tests should cover nftables, BPF, and flowtable chain types, optional device names, function/module strings, priority formatting, and nested descriptions.
