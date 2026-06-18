# sources/user-network-fs/samba/source4/libcli/rap/rap.c

Purpose: implements client-side RAP/LANMAN remote administration protocol calls over SMB transactions to `\\PIPE\\LANMAN`.

Important APIs: `new_rap_cli_call()`, `rap_cli_do_call()`, and many `smbcli_rap_*` wrappers for share enumeration, server enumeration/info, print queue/job/destination operations, user password changes, user get/add/delete, session enum/getinfo, and remote time-of-day.

Control flow: each wrapper creates a `rap_call`, pushes RAP parameter descriptor characters and scalar/string/data arguments, sets expected data and auxiliary formats, calls `rap_cli_do_call()`, then pulls RAP status, convert offsets, counts/availability, and typed output structures. `rap_cli_do_call()` assembles call number, descriptor strings, parameter blob, data blob, and optional aux descriptor into an SMB transaction to `\\PIPE\\LANMAN`; response blobs become NDR pull contexts.

State and persistence: `rap_call` owns push/pull contexts and descriptor strings for one call. Operations can change remote server state, such as print job pause/delete, queue purge, password changes, and user add/delete. Local persistence is absent.

Dependencies and integration: depends on `libcli.h`, raw SMB transaction support, generated RAP NDR definitions, and libndr. It is built as `LIBCLI_RAP`.

Risks: RAP uses legacy ASCII/no-align formats and convert offsets; malformed or hostile responses can exercise offset and bounds handling. Some format comments admit uncertainty. Password-changing functions handle encrypted buffers and should avoid debug leakage. Test signals include level-specific format coverage, invalid level rejection, convert-offset string pulls, count/available parsing, print job control calls, user management calls, and debug NDR print behavior at high log levels.
