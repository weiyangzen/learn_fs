# sources/security-integrity/selinux/secilc/secil2conf.8.xml
# sources/security-integrity/selinux/secilc/secil2conf.8.xml

Purpose: DocBook source for the `secil2conf(8)` manpage.

Important APIs and control flow: documents command synopsis, purpose, options (`--output`, `--mls`, `--preserve-tunables`, `--qualified-names`, `--verbose`, `--help`), and see-also links to `secilc`, `sestatus`, generated HTML/PDF docs, and the CIL design wiki. `secilc/Makefile` converts it to a manpage with `xmlto man`.

State and persistence: source XML persists in repo; generated `.8` manpage is build output.

Dependencies and integration points: depends on DocBook/XML toolchain and is installed with secilc utilities.

Risks and test signals: option text must track the actual `secil2conf` implementation. XML validity/build success is the primary automated signal.
