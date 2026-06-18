# File Research: sources/local-fs/xfsdump/po/Makefile

Localization Makefile.

Behavior:
- Sets POT file to `$(PKG_NAME).pot`.
- Defines supported `LINGUAS = de pl`.
- Builds `.pot` and `.mo` files by default.
- Uses `$(LOCALIZED_FILES)` as gettext input.
- `install` invokes `$(INSTALL_LINGUAS)`.
- `install-dev` and `install-lib` are empty.

Role:
- Integrates German and Polish translations into the package build.
