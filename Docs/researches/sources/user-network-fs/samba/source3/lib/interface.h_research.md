# sources/user-network-fs/samba/source3/lib/interface.h

Purpose: declares source3 network-interface query and lifecycle functions.

Important APIs/types/functions: interface option flags, local address/net predicates, count/accessor helpers, load/free/change functions, and ifindex option lookup.

Control flow: callers load global interface state and then query addresses, broadcasts, and interface metadata.

State/persistence behavior: returned pointers refer to process-global state owned by `interface.c`.

Dependencies/integration: used by smbd/nmbd networking and FSCTL network interface reporting.

Risks/test signals: callers need initialized state and must not free returned pointers. Interface parsing/bind tests validate the contract.
