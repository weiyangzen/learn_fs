# sources/user-network-fs/davfs2/etc/davfs2.conf

## Purpose
This is the installed template/default configuration file for davfs2. It lists supported options and default values, almost entirely commented out, for administrators and users to enable as needed.

## Important options
It groups options into general daemon settings (`dav_user`, `dav_group`, `buf_size`), WebDAV behavior (`use_proxy`, certificates, secrets, auth prompts, locks, ETags, cookies, redirects, timeouts, retries, headers), cache behavior (`backup_dir`, `cache_dir`, `cache_size`, refresh intervals, upload delay, GUI optimization, memory minimization, lookup sync), and debug categories.

## Control flow
There is no executable flow. The runtime parser in davfs2 consumes uncommented keyword/value lines from system and user config files, with mount-specific sections documented elsewhere.

## State and persistence behavior
When installed, this file becomes part of persistent system configuration under the davfs2 sysconf directory. Most lines are comments and therefore do not override compiled defaults until edited.

## Dependencies and integration points
It is installed by `etc/meson.build` and should stay aligned with `man/davfs2.conf.5.in` and the runtime option parser. It references cache directories, secrets files, cert directories, and syslog debug behavior.

## Risks
Default drift is visible: this template says `buf_size 64`, while the manpage states default 16. It also lists `sync_on_lookup`, which is not covered in the read English manpage. Documentation/config drift can make administrator expectations wrong. Debug options can expose secrets if enabled.

## Test signals
Package installation tests should verify the file lands in the expected sysconf directory. Parser tests should load representative uncommented options and mount-specific sections. Documentation checks should compare option names/defaults between this template, manpage, and parser tables.
