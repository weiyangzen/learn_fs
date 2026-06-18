## sources/security-integrity/audit-userspace/audisp/plugins/Makefile.am

Purpose: plugin subdirectory selection for audit dispatcher plugins.

It always builds af_unix, remote, syslog, and filter, adds ids/statsd under `ENABLE_EXPERIMENTAL`, and z/OS remote under `ENABLE_ZOS_REMOTE`. State is build traversal only. Dependencies are configure conditionals. Risks are feature-gated plugins missing regular build coverage unless CI enables flags. Test signal is CI configure enabling experimental and z/OS remote.
