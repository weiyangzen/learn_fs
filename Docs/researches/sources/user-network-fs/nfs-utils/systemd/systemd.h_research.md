# sources/user-network-fs/nfs-utils/systemd/systemd.h

Purpose: `systemd.h` declares the shared systemd generator helper API.

Important APIs and types: It exposes `char *systemd_escape(char *path, char *suffix)` and `int systemd_in_initrd(void)`.

State, dependencies, and integration: The header owns no state. Callers must free the string returned by `systemd_escape`. It is included by the systemd generator sources.

Risks and test signals: There is no include guard in this snapshot. Tests should compile all generator sources together and validate callers free returned names on all paths.
