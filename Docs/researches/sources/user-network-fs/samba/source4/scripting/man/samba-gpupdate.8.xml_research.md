<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/man/samba-gpupdate.8.xml -->
# sources/user-network-fs/samba/source4/scripting/man/samba-gpupdate.8.xml

Purpose: DocBook manpage source for `samba-gpupdate(8)`.

Important APIs/types/functions: DocBook `refentry`, `refmeta`, `refsynopsisdiv`, option paragraphs, and manual metadata version `4.8.0`.

Control flow: static documentation describes the command synopsis, purpose, supported options, Samba common options, credential options, version option, and author section.

State and persistence behavior: no runtime state; it is transformed into a manpage when manpage generation is enabled.

Dependencies and integration points: installed by `source4/scripting/wscript_build` through `bld.MANPAGES` when `XSLTPROC_MANPAGES` is enabled.

Risks: documented command name title uses `SAMBA_GPOUPDATE`, which differs from `samba-gpupdate`. Option text can drift from actual command implementation.

Test signals: successful DocBook/XML validation and generated `samba-gpupdate.8` content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/man/samba-gpupdate.8.xml -->
