## sources/user-network-fs/nfs-utils/utils/statd/statd.h

Purpose: Shared statd declarations, constants, global state accessors, and mode flags.

Important APIs/types/functions: Includes RPC `sm_inter.h`, defines `STAT_FAIL`/`STAT_SUCC`, declares hostname helpers, service loop, notification processors, socket/state helpers, allocation helpers, and exports `SM_stat_chge` through `MY_NAME` and `MY_STATE`. Defines timeout constants and mode flags.

Control flow: No executable flow; establishes contracts across statd compilation units.

State and persistence: Exposes global NSM local name/state and run mode. Persistent state is handled by declared helpers.

Dependencies and integration: Included by all statd sources; depends on generated NSM RPC headers and nfs-utils logging/system abstractions.

Risks and test signals: Global macros make hidden coupling easy. Compile-time tests and integration tests should ensure every source sees consistent mode/timeout/state definitions.
