# sources/user-network-fs/samba/source3/utils/net_registry_util.h

## Purpose
This header declares registry utility functions used by local `net registry` commands.

## Important APIs, Types, And Control Flow
It declares `print_registry_key()`, `print_registry_value()`, `print_registry_value_with_name()`, and `split_hive_key()`. The declarations depend on registry-facing types such as `NTTIME`, `struct registry_value`, `WERROR`, and `TALLOC_CTX` being available from prior includes.

## State And Persistence
There is no header state. The declared functions only format output or return allocated hive/subkey strings to callers.

## Dependencies And Integration Points
This header is included by `net_registry.c` and implemented by `net_registry_util.c`. It forms the shared contract for path splitting and consistent value/key display.

## Risks And Test Signals
The include guard is local (`__NET_REGISTRY_UTIL_H__`) and the header does not include the type definitions it references, so include order matters. Test signals are compile coverage in translation units that already include registry and talloc definitions, plus behavioral tests through the utility implementation.
