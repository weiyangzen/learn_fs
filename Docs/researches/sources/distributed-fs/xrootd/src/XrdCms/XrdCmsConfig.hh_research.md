# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsConfig.hh

## Purpose

`XrdCmsConfig.hh` declares `XrdCmsConfig`, the global cmsd configuration/job object. It is both the startup coordinator and the shared runtime configuration record consumed by cluster management, cache behavior, filesystem setup, scheduling, security, preparation, and admin subsystems.

## Important APIs and types

- `XrdCmsConfig : public XrdJob` so phase-two startup can schedule `DoIt()` asynchronously.
- Public startup methods: `Configure0()`, `Configure1()`, `Configure2()`, `ConfigXeq()`, and `DoIt()`.
- Utility/status methods: `GenLocalPath()`, `asManager()`, `asMetaMan()`, `asPeer()`, `asProxy()`, `asServer()`, and `asSolo()`.
- Public configuration fields cover delay policy, query policy, server-count/service thresholds, load and scheduling weights, disk thresholds, role flags, ports/sockets, exported paths, plugin names/parameters, local/remote roots, identity fields, security/admin sockets, filesystem programs, and statistics flags.
- Private helpers and directive parsers are declared for defaults, plugin setup, config scanning, manifest writing, role-specific setup, system id generation, and all supported `cms.*` directives.
- Namespace externs publish `XrdCms::Admin`, `XrdCms::Config`, and `XrdCms::Sched`.

## Control flow and state shape

The class exposes many fields directly because existing CMS components read configuration without accessor indirection. The constructor calls `ConfigDefaults()` and labels the job `"cmsd startup"`. Startup is expected to proceed through `Configure0`, `Configure1`, `Configure2`, then scheduled `DoIt()`.

The public fields can be grouped by behavior: delay and service policy; performance/scheduling weights and limits; disk/space thresholds; role/network/admin identity; plugin and path mapping; exported paths; and filesystem operation programs. These values are read by cluster selection, manager setup, state reporting, and server login flows.

## State and persistence behavior

`XrdCmsConfig` is long-lived global state. It owns many heap strings and subsystem pointers but has an empty destructor, reflecting process-lifetime ownership. Some values are static defaults until config parsing changes them; others are runtime dynamic knobs changed through `ConfigXeq()` for the dynamic directives. Persistent effects are implemented in the `.cc` file, mainly socket creation, plugin loading, environment exports, and manifest append.

## Dependencies and integration points

The header includes `XrdJob`, CMS path list/types, OUC path/text lists, and forward-declares scheduler, networking, OSS, stream, admin, security, environment, name mapping, and program types. It is included across CMS modules wherever global configuration is needed. `XrdCmsCluster` uses delay, scheduling, role, disk, and peer settings extensively; `XrdCmsManager`, `XrdCmsState`, `XrdCmsCache`, `XrdCmsPrepare`, and security/OSS setup also depend on it.

## Risks

- The large public mutable field surface makes invariants implicit. For example, changing `SUPCount`, `SUPLevel`, or scheduling fields can alter cluster behavior without local validation.
- Empty destructor and process-lifetime ownership are acceptable for daemon startup but complicate leak-sanitizer expectations and unit-test reuse.
- Several fields use small integer or `char` types for boolean/config modes, so parser range checks in the implementation are critical.
- Dynamic directives share the same object as startup-only state; future dynamic additions must audit whether downstream subsystems observe changes safely.

## Test signals

Tests should verify constructor defaults, role accessor methods, phase-order assumptions, dynamic-vs-static directive dispatch, bounds on small fields, and downstream behavior when cluster selection reads scheduling/space/delay fields. Leak tests should account for intended process-lifetime allocations or instantiate in a controlled harness with cleanup wrappers.
