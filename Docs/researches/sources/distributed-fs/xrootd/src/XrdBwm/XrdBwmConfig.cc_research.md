# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmConfig.cc

Purpose: parses BWM configuration directives and wires authorization, policy, tracing, and logging into the plugin.

Important APIs/types/functions: `XrdBwm::Configure`, `ConfigXeq`, `xalib`, `xlog`, `xpol`, `xtrace`, `setupAuth`, and `setupPolicy`. Parser macros dispatch recognized directives: `authorize`, `authlib`, `log`, `policy`, and `trace`.

Control flow: `Configure` enables full tracing from `XRDDEBUG`, optionally opens the config file, captures BWM config lines, and applies `bwm.` directives. It then conditionally initializes authorization, chooses a loaded custom policy or default `XrdBwmPolicy1`, starts the logger, and registers policy/logger with `XrdBwmHandle`. `xpol` supports either `maxslots in out` or `lib path [params]`.

State and persistence: mutates singleton fields: auth library/parameters, logger object, policy library/parameters, slot counts, trace mask, and authorization/policy pointers. No data persists outside process memory.

Dependencies and integration points: uses `XrdOucStream`, `XrdOuca2x`, `XrdOucPinLoader`, XrdAcc default authorization, BWM policy plugin entry point `XrdBwmPolicyObject`, and XRootD logging.

Risks: if no config file is specified, it logs an error but continues with defaults because the `if` lacks braces around the `else` pairing style but is syntactically intentional. Custom policy loader object lifetime is subtle; unloading is avoided when objects must remain valid. `xlog` accepts program/socket/log targets but validation is deferred.

Test signals: no-config defaults, invalid config file, each directive, bad slot values, default policy creation, custom policy/auth load failures, trace option accumulation/off, and logger startup failures.
