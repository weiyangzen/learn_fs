# sources/user-network-fs/nfs-utils/tests/nfsconf/02-valid.conf

Purpose: `02-valid.conf` is a positive nfs.conf parser fixture covering sections, subsection labels, quoting, whitespace, variable expansion, duplicate sections, and includes.

Important content and control flow: It defines `[environment]`, `[section_one]`, and repeated `[section_two "..."]` blocks. Values include `$three`, quoted strings with extra whitespace, keys containing spaces, and an `include = "02-valid.sub"` directive.

State, dependencies, and integration: Test state comes from parser output and the included subfile. It integrates with `t0002-nfsconf.sh` or nfsconf tooling.

Risks and test signals: If include files are missing from distribution or `srcdir`, tests become path-sensitive. Assertions should verify expansion, trimming, duplicate section merge/override behavior, subsection selection, and include resolution.
