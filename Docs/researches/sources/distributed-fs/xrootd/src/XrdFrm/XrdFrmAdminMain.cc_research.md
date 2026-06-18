<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminMain.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminMain.cc

## Purpose
`XrdFrmAdminMain.cc` is the entry point for `frm_admin`. It configures the process, selects command-line or interactive mode, manages readline history, and dispatches commands to the global admin object.

## Important Objects And Functions
The file defines global `XrdFrm::Config` for the admin subsystem, global `XrdFrm::Admin`, and compatibility globals `XrdLog` and `XrdTrace` needed by linked xrootd components. If GNU readline is unavailable, it provides fallback `readline`, `add_history`, and `stifle_history` stubs. `main()` handles signal masking, logger binding, configuration, argument mode selection, interactive tokenization, and final exit.

## Control Flow And State
`main()` ignores SIGPIPE and blocks SIGPIPE/SIGCHLD before configuration. It calls `Config.Configure()`, exits with code 4 on failure, then either dispatches a single command from argv or loops over interactive commands from `frm_admin> `. Interactive commands are tokenized with `XrdOucTokenizer`; repeated identical lines are not added to history. `Admin.Quit()` exits with `finalRC`.

## Dependencies And Integration Points
This file integrates `XrdFrmConfig`, `XrdFrmAdmin`, `XrdFrcTrace`, `XrdNet` socket options, `XrdSysLogger`, optional readline, and xrootd global trace/error symbols.

## Risks And Test Signals
Fallback `readline()` returns null on empty lines, causing an empty line to quit rather than just reprompt. Interactive tokenizer behavior should be tested for quoted arguments and command abbreviations. Signal masking and logger setup are process-level behaviors. Tests should run `frm_admin -h`, invalid config, one-shot commands, and an interactive session with help, invalid command, repeated command, empty input, and quit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminMain.cc -->
