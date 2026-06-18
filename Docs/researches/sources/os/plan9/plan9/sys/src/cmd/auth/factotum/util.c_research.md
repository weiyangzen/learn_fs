# File Research: sources/os/plan9/plan9/sys/src/cmd/auth/factotum/util.c

Large shared utility layer for factotum. It covers network/auth dialing, secstore dialing, console prompting, key insertion/replacement, key matching, protocol lookup, nvram key conversion, authinfo serialization, capability creation, and attr manipulation.

`findkey` is central: it combines current attrs with extra query attrs, checks ownership, skips disabled keys unless requested, handles confirmation through `canusekey`, and returns `RpcNeedkey` with a sorted query string when prompting is allowed. `matchattr` implements query/nameval/default matching across public and private attrs.

Security-related helpers include `private` setup elsewhere, `mkcap` using `#¤/caphash`, `disablekey` after failed authentication, zeroing selected secrets, and owner/secstore host derivation through `writehostowner`. `memrandom` uses `fastrand`, so protocol callers relying on it inherit that randomness quality.
