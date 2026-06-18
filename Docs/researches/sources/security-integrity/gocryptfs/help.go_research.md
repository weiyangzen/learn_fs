# sources/security-integrity/gocryptfs/help.go

Purpose: This file renders short and long command-line help for gocryptfs.

Important APIs and functions: `tUsage` contains the usage template. `helpShort()` prints concise syntax and common options. `helpLong()` prints extended option descriptions, notes, and compatibility guidance.

Control flow and state: Help functions write to stdout/stderr and exit behavior is controlled by callers in CLI parsing. No persistent state is changed.

Dependencies and integration points: Integrated with `parseCliOpts`, `-h`, `-hh`, and syntax-error paths. Text must stay aligned with registered flags in `cli_args.go`.

Risks and test signals: Drift between help text and actual flags confuses users. Signals include help-output tests or manual checks after CLI changes.
