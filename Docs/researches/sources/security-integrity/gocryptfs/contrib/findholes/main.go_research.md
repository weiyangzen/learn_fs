# sources/security-integrity/gocryptfs/contrib/findholes/main.go

Purpose: This CLI wraps the `holes` package to create, inspect, print, and verify sparse-file hole maps.

Important APIs and functions: It parses command-line arguments, opens the target file, optionally creates a sparse fixture, calls `holes.Find`, prints `holes.PrettyPrint`, and invokes verification.

Control flow and state: The command mutates a file only in create mode; otherwise it reads seek metadata from an opened descriptor. Exit status reflects open/find/verify errors.

Dependencies and integration points: Used manually against gocryptfs and underlying filesystems to compare sparse-file support.

Risks and test signals: Filesystem-dependent semantics may look like failures. Signals are stable hole/data segment output and successful verification over the same file descriptor.
