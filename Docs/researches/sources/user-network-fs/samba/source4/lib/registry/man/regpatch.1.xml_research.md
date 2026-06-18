# sources/user-network-fs/samba/source4/lib/registry/man/regpatch.1.xml

This DocBook man page documents `regpatch`, which applies registry patches to Windows registry files. The synopsis accepts `PATCHFILE`, includes Samba common options, and documents `--backend BACKEND` and `--credentials=CREDENTIALS`. It states that if no patch file is specified, patch data is read from standard input.

The page has no runtime control flow, but it describes the user-facing wrapper around `reg_diff_apply()` and patch loaders such as `.REG` and PReg support. Persistence is mutation of the target registry backend or file. Integration points are `regdiff`, `regtree`, `regshell`, Samba credential parsing, and backend loading.

Risks are user-impacting because applying patches mutates registry data; documentation should be precise about input format, stdin behavior, and backend selection. Test signals include manpage generation, `regpatch --help`, applying a `.REG` file from disk and stdin, and verifying modified output with `regtree` or `regdiff`.
