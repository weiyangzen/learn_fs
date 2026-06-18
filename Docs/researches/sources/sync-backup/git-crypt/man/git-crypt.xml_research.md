# sources/sync-backup/git-crypt/man/git-crypt.xml

Purpose: DocBook XML source for the `git-crypt(1)` manual page.

Important APIs/types/functions: DocBook `refentry` structure with metadata, synopsis sections, command descriptions for `init`, `status`, `add-gpg-user`, `unlock`, `export-key`, `help`, and `version`, usage guidance, `.gitattributes` rules, multiple-key support, and see-also links.

Control flow: documentation flow introduces transparent Git encryption, lists command synopses, describes each command and option, then provides setup/share/unlock workflow and attribute examples.

State/persistence behavior: describes persistent states rather than implementing them: encrypted files in Git history, `.gitattributes` rules, committed `.git-crypt` GPG-encrypted key files, and exported symmetric keys. The generated manpage is produced by the Makefile's `build-man` target.

Dependencies/integration: consumed by `xsltproc` with DocBook XSL to generate `man/man1/git-crypt.1`. It should stay aligned with `git-crypt.cpp` usage/help and `commands.cpp` implemented options.

Risks/test signals: documentation can drift from implementation; notably not all stubbed commands are documented as available. Tests/signals include successful DocBook validation/generation, checking command option parity, and verifying version/date/product metadata during release.
