# File Research: sources/local-fs/xfsdump/librmt/rmtaccess.c

Implements `rmtaccess(path, amode)`.

Behavior:
- If `_rmt_dev(path)` says the path is remote, returns success without contacting the host.
- Otherwise delegates to local `access(2)`.

Implication:
- Remote access checks are deferred to remote open/operation time.
