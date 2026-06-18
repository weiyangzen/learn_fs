## sources/security-integrity/audit-userspace/audisp/plugins/af_unix/af_unix.conf

Purpose: default audisp plugin config for AF_UNIX event socket forwarding.

It is inactive by default, runs `/sbin/audisp-af_unix`, type `always`, passes mode/path/format args (`0640 /run/audit/audispd_events string`) with optional queue depth, and receives binary dispatcher format. State is installed under plugins.d and parsed by `audispd-pconfig.c`. Risks include default path/binary mismatch on usr-merged systems and inactive default hiding test coverage. Test signal is enabling config and connecting a client to the socket.
