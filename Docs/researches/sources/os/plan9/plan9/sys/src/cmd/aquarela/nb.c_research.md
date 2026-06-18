# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nb.c

Initializes global NetBIOS state.

Key data:
- `NbGlobals nbglobals`
- `NbName nbnameany = { '*' }`

Key function:
- `nbinit` installs IP and NetBIOS-name formatters, reads `/net` interface data, records local IP, computes broadcast IP, and sets the local NetBIOS name from `sysname()`.

Interactions:
- Required before NetBIOS datagram, name service, and session service operation.

Notable details:
- Broadcast address is computed by OR-ing IP bytes with inverse mask bytes.
