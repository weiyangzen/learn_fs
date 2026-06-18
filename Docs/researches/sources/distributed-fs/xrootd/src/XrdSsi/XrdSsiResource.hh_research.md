# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiResource.hh

Purpose: defines `XrdSsiResource`, the provider-facing description of a resource needed for SSI request execution. It carries resource name, user, routing hints, client identity, affinity, and handling options.

Important APIs/types: public fields are `rName`, `rUser`, `rInfo`, `hAvoid`, `client`, `affinity`, and `rOpts`. `Affinity` values are `Default`, `None`, `Weak`, `Strong`, and `Strict`. Resource options are `Reusable` and `Discard`. The constructor initializes all fields with defaults and sets `client` to null.

Control flow and state: this is a simple value-like data holder using owning `std::string`s for text fields and a borrowed `XrdSsiEntity *` for identity. There are no methods beyond constructor/destructor and no persistence.

Dependencies and integration: consumed by `XrdSsiProvider::QueryResource()`, `XrdSsiService::Prepare()/ProcessRequest()`, and concrete `XrdSsiFileResource`. Risks include public mutable fields, ambiguous ownership of `client`, and providers retaining borrowed pointers beyond lifetime. Test signals should cover constructor defaults, option bit combinations, affinity interpretation in client routing code, and copied resource behavior.
