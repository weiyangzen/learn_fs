## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/LoadBalance.h

Purpose: This is a compatibility include wrapper that exposes the generated/source actor implementation in `LoadBalance.actor.h` under the traditional `LoadBalance.h` name.

Important APIs/types/functions: It defines no new API; every public symbol comes from `LoadBalance.actor.h`, including `loadBalance()`, `basicLoadBalance()`, `LoadBalancedReply`, and comparison helpers.

Control flow: Include-time only. Consumers including this header enter the actor-header include logic, which switches to `LoadBalance.actor.g.h` when compiled with the actor compiler generated output.

State and persistence behavior: None in this file.

Dependencies and integration points: This file is the integration point for code that does not want to include the `.actor.h` path directly. It inherits all actor compiler requirements and dependencies from `LoadBalance.actor.h`.

Risks: Any include-cycle or actor generated-header issue appears here for legacy include users. Because it lacks its own include guard, it relies on `LoadBalance.actor.h` guards.

Test signals: Build coverage is the primary signal: any translation unit including `fdbrpc/LoadBalance.h` should compile in both actor-compiler and non-intellisense paths.
