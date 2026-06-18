# sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp_pm.h

Purpose: auto-generated generic netlink UAPI for the MPTCP path manager family, covering endpoint management commands, limits, subflow operations, and event notifications.

Important APIs/types/functions: exports family name/version, `enum mptcp_event_type`, endpoint address attributes, subflow attributes, path-manager attributes, event attributes, and commands from add/delete/get/flush addresses through set flags, announce/remove, and subflow create/destroy.

Control flow: userspace sends MPTCP PM netlink commands to manage local/remote endpoint state and listens for events such as connection created/established/closed, announced/removed addresses, subflow establishment/closure/priority, and listener lifecycle.

State/persistence behavior: commands mutate path-manager state in the network namespace and can trigger MPTCP signaling or subflow lifecycle changes. Events are transient notifications carrying tokens, IDs, addresses, ports, flags, and errors.

Dependencies/integration: generated from `mptcp_pm.yaml` and included by `mptcp.h`. Integrates with generic netlink, MPTCP sockets, endpoint flags, and user path managers.

Risks and test signals: sparse event numbering and nested address attributes can break decoders. Tests should cover command names, endpoint attrs, event attrs including reset reason/server-side flags, and subflow token/sequence attributes.
