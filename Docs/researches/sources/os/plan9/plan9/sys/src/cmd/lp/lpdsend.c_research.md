# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/lpdsend.c

Read fully: 439 lines, 9580 bytes. SHA-256 prefix: `731f608ac4611f2f`.

This is an LPD client sender. It connects to a remote printer service, optionally queries queue status, kills a job, or sends a print job using LPD control/data file protocol.

Important routines:
- `copyfile()` copies data with timeout and progress messages.
- `killjob()` sends LPD remove-job command.
- `checkqueue()` sends queue status command and copies response to stderr.
- `getack()` validates single-NUL acknowledgements.
- `senddata()` and `sendctrl()` send LPD data/control files.
- `sendjob()` starts a receive-printer-job request and sends data then control.
- `netmkaddr()` fills default network/service components.
- `main()` parses options, prepares stdin/file input, dials remote printer from reserved source ports 721-731, gets hostname, and dispatches action.

Risk notes: `tmpnam()` is used for stdin temp files on non-Plan 9 path. Source-port retry is hardcoded. Option `-t` switch appears to test current `filetype` rather than `optarg[0]`, which may be a historical bug.
