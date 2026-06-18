# sources/user-network-fs/samba/source4/lib/registry/man/regdiff.1.xml

This DocBook man page documents `regdiff`, a command that compares two Windows registry files key by key and emits a patch format that `regpatch` can apply. The synopsis includes common Samba command-line option includes plus `--backend BACKEND` and `--credentials=CREDENTIALS`. It states that `regdiff` and `regpatch` use the same format as Windows `.REG` files.

There is no executable control flow, but the document is an integration contract for command-line behavior and supported workflows: compare registry backends, generate a diff, and later apply it. Persistence is through the input registry files and generated patch file.

Risks are documentation drift from actual tool behavior, especially backend names, authentication behavior, and patch format support. The page references version 4.0 and related tools. Test signals include generated manpage build, `regdiff --help` matching documented options, and end-to-end diff/apply tests with `regpatch`.
