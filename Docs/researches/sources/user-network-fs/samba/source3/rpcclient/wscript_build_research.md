# sources/user-network-fs/samba/source3/rpcclient/wscript_build

Purpose: this Waf build fragment defines the Samba3 `rpcclient` binary.

Important APIs, types, and functions: it calls `bld.SAMBA3_BINARY('rpcclient', source=..., deps=...)`. The source list contains `rpcclient.c` and every command module, including SPOOLSS, SRVSVC, WKSSVC, WINREG, WITNESS, Spotlight, and UNIXINFO.

Control flow: build-time only. Waf evaluates the script and compiles the listed C files into one binary with the listed dependency libraries.

State and persistence: no runtime state. It affects generated build outputs and link dependency closure.

Dependencies and integration: dependencies include command-line support, pdb, libsmb, smbconf, NDR libraries, RPC client libraries, SMBREADLINE, ADS, schannel, DCUTIL, interface-specific RPC NDR libs, mdssvc, and UNIXINFO.

Risks: adding a command source without its matching dependency can create link failures. Removing a source from this list silently removes commands from the binary even if the source still builds elsewhere.

Test signals: run the configured Waf build, inspect `rpcclient -c help`, and verify all command groups from the source list appear.
