## sources/user-network-fs/nfs-utils/utils/statd/notlist.h

Purpose: Declares statd notification-list data structures, globals, functions, and accessor macros.

Important APIs/types/functions: `struct notify_list` embeds `mon`, callback port, retry count, state, DNS name, linked-list pointers, XID, and timeout. Declares global `rtnl` and `notify`, list functions, and `NL_*` macros for nested NSM fields.

Control flow: No executable flow; macros define how all list users read/write monitor identity and scheduling fields.

State and persistence: Defines in-memory state only. `rtnl` mirrors monitored records; `notify` tracks pending RPC work.

Dependencies and integration: Includes `netinet/in.h` and depends on NSM types/macros from `statd.h`.

Risks and test signals: Macro-heavy access can obscure ownership and type errors. Tests should compile all users and validate field preservation through clone/insert/remove workflows.
