## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurgMain.cc

Purpose: provides the `frm_purge` executable entry point. It parses daemon/one-shot options through `XrdFrmConfig`, installs logging and signal defaults, builds purge policies, and drives repeated purge cycles.

Important APIs and control flow: `main()` blocks signals, sets thread stack size, calls `Config.Configure(argc, argv, &mainConfig)`, displays configuration, then either performs one purge pass for `-O` mode or loops forever. The loop honors `Config.StopPurge` by sleeping while the stop file exists. `mainConfig()` converts configured policy records into `XrdFrmPurge::Policy()` objects, ensures a `public` policy and policies for all spaces, applies one-time overrides through `XrdFrmPurge::Init()`, and starts a UDP server placeholder thread for daemon mode.

State and persistence: process state is global `XrdFrm::Config`, `XrdLog`, and `XrdTrace`. The command may create/administer PID/log files via configuration, and purge actions persist through filesystem deletions performed by `XrdFrmPurge`.

Dependencies and integration: integrates `XrdFrmConfig`, `XrdFrmPurge`, XrdNet socket creation for admin path, and XrdSys logging/thread utilities. `mainServer()` is currently a stub with server logic commented out.

Risks and test signals: command-line behavior is safety-sensitive because `-T` test mode disables actual purge and clears fix mode. Tests should cover one-shot argument validation, stop-file suspension, missing policy defaults, disabled spaces, UDP socket startup, and that test mode prevents destructive `Config.Fix`.
