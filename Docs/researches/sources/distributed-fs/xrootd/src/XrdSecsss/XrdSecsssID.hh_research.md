# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssID.hh

Purpose: public interface for applications to configure SSS client identity mapping before connecting to SSS-enabled servers.

Important APIs and types: `authType` enumerates dynamic, mapped, mapped mutual, static, and static mutual modes. The constructor installs the singleton mapper with optional default identity and contact tracker. `Register()` creates, replaces, or deletes login-ID mappings.

Control flow: users create one instance before connections. The protocol later calls private `getObj()` and `Find()` to determine whether credentials are static, mapped, or mutual-authenticated.

State and persistence: declares default identity pointer, auth type, static/mapped flag, and tracking flag. Actual registry state is implemented in `XrdSecsssID.cc`; no disk persistence.

Dependencies and integration: forward declares `XrdSecEntity`, `XrdSecsssCon`, and `XrdSecsssEnt`, keeping the public header light. Applications must link with `libXrdUtils.so`.

Risks: comments note the object cannot be deleted once created, effectively making it process-global configuration. Mutual authentication depends on login IDs matching server-returned values unless mapped modes override lookup.

Test signals: API compile tests in external clients, construction with every auth type, register failure in static mode, and integration with protocol credential generation.
