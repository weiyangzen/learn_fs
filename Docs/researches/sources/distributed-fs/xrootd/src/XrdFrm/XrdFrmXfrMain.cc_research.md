## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrMain.cc

Purpose: provides the shared main program for transfer daemon and agent personas. The executable behaves as `frm_xfrd` when named accordingly; otherwise it runs in agent mode.

Important APIs and control flow: `main()` blocks signals, sets stack size, determines persona from `argv[0]`, configures logging, calls `Config.Configure(argc, argv, &mainConfig)`, then exits with `XrdFrmXfrAgent::Start()` or `XrdFrmXfrDaemon::Start()`. `mainConfig()` initializes the daemon only when not in agent mode; agents defer initialization to `Start()`.

State and persistence: global `XrdFrm::Config`, `XrdLog`, and `XrdTrace` are instantiated for the transfer subsystem. Daemon mode persists queue/lock state through downstream components.

Dependencies and integration: integrates `XrdFrmConfig`, `XrdFrmXfrAgent`, `XrdFrmXfrDaemon`, and XrdSys logging/thread utilities. Command-line options include background daemon mode, config, debug, fix, log rotation, instance/site names, test mode, verbosity, and log flushing.

Risks and test signals: persona detection uses `strncmp("frm_xfrd", pP, 8)`, so symlink/binary names drive behavior. Tests should cover agent/daemon naming, configuration callback return inversion, invalid config exit code, and test-mode propagation.
