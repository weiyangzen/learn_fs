# sources/user-network-fs/samba/source3/lib/netapi/examples/netdomjoin-gui/netdomjoin-gui.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/netdomjoin-gui/netdomjoin-gui.c

Purpose: Provides a GTK graphical sample for viewing and changing Samba/Windows-style computer name, workgroup/domain membership, description, and join options.

Important APIs/types/functions: `join_state` stores libnetapi context, GTK widgets, current/new join names, credentials, description, hostname/domain details, server role, and change flags. Key callbacks include credential prompts, description changes, join/unjoin flow, OU scanning, hostname/domain/workgroup entry handlers, and UI construction. NetAPI calls include `NetServerGetInfo()`, `NetServerSetInfo()`, `NetGetJoinInformation()`, `DsGetDcName()`, `NetGetJoinableOUs()`, `NetJoinDomain()`, `NetUnjoinDomain()`, and partly disabled `NetRenameMachineInDomain()`.

Control flow: `main()` initializes GTK and join state, parses options, initializes libnetapi credentials, gathers server properties/join status, draws the main window, and enters `gtk_main()`. User actions mutate `join_state`, may prompt for credentials, discover DCs/OUs, perform unjoin/join, update labels, and show modal error/info dialogs.

State and persistence behavior: Maintains in-process GUI state and mutates remote/local machine state through NetAPI calls. Credential strings are stored in heap memory until cleared. Successful join/unjoin marks settings changed and prompts for reboot.

Dependencies and integration points: Bridges GTK/glib widgets and libnetapi domain-join APIs. Reuses common NetAPI concepts from CLI examples but owns custom UI state.

Risks: Old GTK API usage, manual memory management, modal callback complexity, and disabled hostname rename path. Credentials live in process memory. Operations can change domain trust and require reboot.

Test signals: Manual/GUI integration tests should cover initialization on workgroup/domain hosts, credentials prompt cancel/continue, OU scan, join failure/success, unjoin, description change, and cleanup on exit.
