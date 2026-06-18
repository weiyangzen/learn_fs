# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/raperrstr.c

Remote Administration Protocol error-code table and formatter. Covers common LAN Manager, share, user/group, print, service, DFS, domain, and remoteboot errors. `raperrstr` returns `"rap: message"` or an unknown-code fallback.

Used by `trans.c` when RAP calls over `\\PIPE\\LANMAN` return nonzero status other than allowed “more data”.
