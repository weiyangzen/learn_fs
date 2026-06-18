<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson_options.txt -->
# sources/user-network-fs/ksmbd-tools/meson_options.txt

## Purpose

Defines Meson options controlling runtime directory, systemd unit installation, and Kerberos support.

## Important APIs, Types, and Functions

Options are string `rundir`, string `systemdsystemunitdir`, feature `krb5` defaulting disabled, and string `krb5_name` defaulting `krb5`.

## Control Flow

Top-level meson.build reads these options to compute `runstatedir`, choose whether/where to install the unit, resolve krb5 dependencies, and choose MIT versus Heimdal pkg-config names.

## State and Persistence Behavior

No runtime state. Build configuration state is stored in the Meson build directory.

## Dependencies and Integration Points

Integrated by top-level `meson.build` and CI jobs.

## Risks and Edge Cases

Packagers must set `krb5=enabled` explicitly for Kerberos. Empty versus explicit path values change install layout.

## Test Signals

Meson setup with default options, explicit `-Drundir=...`, explicit `-Dsystemdsystemunitdir=...`, and both krb5 dependency names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson_options.txt -->
