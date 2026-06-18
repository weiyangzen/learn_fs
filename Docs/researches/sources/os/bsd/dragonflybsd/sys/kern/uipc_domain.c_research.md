# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_domain.c

## Summary
Protocol domain registration and lookup support for the networking stack.

## Main Responsibilities
- Maintains global `domains` list.
- Initializes each domain's protocol switch entries through `net_init_domain`.
- Registers domains with `net_add_domain`.
- Looks up protocols by family/type or family/protocol/type.
- Broadcasts protocol control-input notifications across domains.

## Important Behavior
`net_init_domain` installs default unsupported handlers for missing protocol and user-request functions, supplies default `pru_sense`, `pru_sosend`, and `pru_soreceive`, then runs per-protocol `pr_init`.

After domain initialization it recomputes `max_hdr` and `max_datalen` from header maxima. `domaininit` ensures `max_linkhdr` is at least 20 early in boot.

## Risks
Domains cannot be unloaded because sockets may retain protocol references. Missing `pr_usrreqs` is a panic. Control-input routing depends on protocol `pr_ctlport` and message dispatch in `uipc_msg.c`.
