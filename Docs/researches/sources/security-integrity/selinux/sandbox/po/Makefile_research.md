# sources/security-integrity/selinux/sandbox/po/Makefile
# sources/security-integrity/selinux/sandbox/po/Makefile

Purpose: manages gettext translation catalogs for sandbox.

Important APIs and control flow: collects `.po` files, filters by `LINGUAS`, builds `.mo` files with `msgfmt`, generates/updates `sandbox.pot` from files listed in `POTFILES` with `xgettext`, supports `refresh-po`, `install`, `clean`, `report`, and empty `test`/`relabel` targets.

State and persistence: generated `.pot`, `.mo`, installed locale files under `$(PREFIX)/share/locale`.

Dependencies and integration points: called from sandbox top-level Makefile; depends on gettext tooling.

Risks and test signals: `POTFILES` must stay accurate or strings disappear from translations. No automated validation beyond `msgfmt` report target.
