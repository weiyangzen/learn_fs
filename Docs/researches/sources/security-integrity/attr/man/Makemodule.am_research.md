## sources/security-integrity/attr/man/Makemodule.am

Purpose: manpage aggregation and symlink installation logic.

It includes man1/man3 fragments and adds an install hook that parses `.Nm` names from installed pages to create same-section symlinks for multi-interface manpages. State is installed manpage symlinks. Dependencies are `awk`, `sed`, shell, and `ln -s`. Risks include fragile roff parsing and duplicate symlink handling. Test signal is `make install` into a DESTDIR and manpage symlink inspection.
