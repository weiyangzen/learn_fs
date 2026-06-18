<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/revampire_ad.sh -->
# sources/user-network-fs/samba/source4/scripting/devel/drs/revampire_ad.sh

Purpose: development shell workflow to re-vampire an AD domain, repair DNS zone templates, and apply FSMO LDIF substitutions.

Important APIs/types/functions: sourced `vars`, `vampire_ad.sh`, `ldbsearch`, zone template copying, `sed`, `rndc reconfig`, and `ldbmodify`.

Control flow: sources environment variables, runs the vampire join script, reads the local NTDS objectGUID, copies and patches DNS zone and named configuration templates, reconfigures BIND, creates a temporary FSMO LDIF from template substitutions, applies it to sam.ldb, and removes the temp file.

State and persistence behavior: mutates local provision files, DNS zone files, named configuration, and sam.ldb FSMO-related records.

Dependencies and integration points: depends on adjacent DRS test templates and `vars`, Samba build-tree tools, sudo, and BIND `rndc`.

Risks: heavily environment-specific and uses `set -x` with potentially sensitive variables. Direct `sudo ldbmodify` and template substitutions can damage a test provision if variables are wrong.

Test signals: successful vampire script, patched zone/named files, `rndc reconfig`, and successful `ldbmodify`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/devel/drs/revampire_ad.sh -->
