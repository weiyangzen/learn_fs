# sources/user-network-fs/libtirpc/tirpc/rpc/auth_unix.h

Purpose: `auth_unix.h` defines the weak UNIX/AUTH_SYS credential structure and XDR routine.

Important APIs, types, and functions: It defines `MAX_MACHINE_NAME`, `NGRPS`, `struct authunix_parms`, alias `authsys_parms`, `xdr_authunix_parms`, and `struct short_hand_verf`.

Control flow: AUTH_SYS credentials carry timestamp, machine name, uid, gid, and supplementary gids. Servers may return an AUTH_SHORT verifier containing a replacement opaque credential for shorthand reuse.

State and persistence behavior: The header declares only wire/data structures. Implementations allocate and marshal machine name and gid arrays.

Dependencies and integration points: It is included by `rpc.h` and used by `authunix_create`, server-side `_svcauth_unix`, and RPC message credential handling.

Risks: The header itself warns the system is weak: credentials are unauthenticated and unencrypted. `NGRPS` and `MAX_MACHINE_NAME` are protocol bounds that must be enforced in XDR. UID/GID type widths must match XDR implementation expectations.

Test signals: Tests should cover max machine name, zero and `NGRPS` gids, over-limit rejection, shorthand verifier decode, and AUTH_SYS interop with NFS/RPC services.
