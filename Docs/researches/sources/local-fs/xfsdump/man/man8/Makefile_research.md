# File Research: sources/local-fs/xfsdump/man/man8/Makefile

Makefile for section 8 administrator manpages.

Behavior:
- Sets `MAN_SECTION = 8`.
- Discovers man pages with `$(shell echo *.8)`.
- Installs to `$(PKG_MAN_DIR)/man8`.
- `install` creates destination directory and invokes `$(INSTALL_MAN)`.
- `install-dev` is empty.

Role:
- Packages xfsdump/xfsrestore administrative documentation.
