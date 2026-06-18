# File Research: sources/local-fs/xfsdump/librmt/rmtwrite.c

Implements `rmtwrite(fildes, buf, nbyte)`.

Behavior:
- Local descriptors call `write(2)`.
- Remote descriptors send `W<nbyte>\n`, write the payload to the pipe, then return remote status.
- Short/failing payload writes abort and set `errno = EIO`.

Role:
- Remote tape write wrapper matching `write(2)`-style usage.
