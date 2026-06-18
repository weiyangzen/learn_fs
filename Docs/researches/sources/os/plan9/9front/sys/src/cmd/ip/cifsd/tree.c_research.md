# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/tree.c

Maintains SMB tree IDs, file IDs, and search IDs. It uses dynamically grown arrays of pointers, assigning one-based IDs with `newid`, clearing slots on delete, and preserving object references through `ref` counters.

`connecttree` maps a requested service/path to a `Share`, validates service type, allocates a `Tree`, and returns a TID. `disconnecttree` and `logoff` release all files/finds associated with active trees.

`getfile`, `getpath`, and `getfind` are the primary request-time resolvers used by `smb.c`, returning SMB error codes such as bad TID/FID through out parameters.
