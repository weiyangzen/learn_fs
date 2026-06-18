# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_ssh/Makefile

Read completely: 29 lines.

This builds `pam_ssh` from `pam_ssh.c` using OpenSSH sources from `${NETBSDSRCDIR}/crypto/external/bsd/openssh/dist`. It links against private `libssh`, local `crypt`, and OpenSSL `crypto`, and marks the private libssh subdir as a dependency.

It disables lint/profile/PIC archive installation and includes the common PAM module rules.

Security/reliability notes: build-only file. The module depends on OpenSSH private interfaces such as `sshkey` and auth-agent helpers.
