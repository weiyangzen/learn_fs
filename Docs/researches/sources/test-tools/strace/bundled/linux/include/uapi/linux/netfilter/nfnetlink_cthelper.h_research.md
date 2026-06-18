# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_cthelper.h

Purpose: defines nfnetlink ABI for userspace connection tracking helper registration, query, deletion, helper policies, tuple metadata, queue number, private data length, and enable/disable status.

Important APIs/types/functions: exports helper status constants, message types `NFNL_MSG_CTHELPER_*`, top-level attributes `NFCTH_*`, policy-set attributes supporting multiple policy entries, policy attributes for name/expect max/timeout, and tuple attrs for L3/L4 protocol numbers.

Control flow: userspace registers helpers with name, tuple, policy, queue, private data size, and status, queries registered helpers, or deletes them.

State/persistence behavior: helper objects are persistent kernel conntrack-helper state and can affect later packet processing and expectation creation until removed or disabled.

Dependencies/integration: uses nfnetlink subsystem `NFNL_SUBSYS_CTHELPER`; integrates with conntrack expectations, userspace helper queues, and nftables ct helper objects.

Risks and test signals: policy sets use repeated numbered attributes and helper status can be changed. Tests should decode nested policy sets, tuple protocol fields, private data length, queue number, status constants, and get/delete messages.
