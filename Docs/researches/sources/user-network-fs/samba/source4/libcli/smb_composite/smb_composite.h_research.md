<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb_composite.h -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/smb_composite.h

Purpose: declares the public data contracts and function prototypes for SMB composite helpers used by source4 clients.

Important APIs and types: `smb_composite_loadfile`, `smb_composite_fetchfile`, `smb_composite_savefile`, `smb_composite_connect`, `smb_composite_sesssetup`, `smb_composite_fsinfo`, `smb_composite_appendacl`, and SMB2 helper prototypes. It includes raw SMB and SMB2 headers and exposes both async send/recv and sync variants where available.

Control flow: the header itself has no executable flow, but its struct layout defines how callers supply credentials, resolver and gensec settings, SMB/session options, service names, filenames, and output ownership. `smb_composite_connect` explicitly models optional session setup with NULL credentials and optional tree connect with NULL service.

State and persistence: outputs are pointer-heavy talloc objects: loaded data, trees, filesystem info, ACL security descriptors, and session IDs. Callers must respect recv ownership rules implemented in the C files.

Risks: ABI/API coupling is high because composite implementations copy these structs directly. Missing fields in `smb_composite_fsinfo` compared with connect options can force option inheritance from another tree. Test signals are compile coverage of all declarations, struct initialization by downstream callers, and ABI expectations around optional fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/smb_composite.h -->
