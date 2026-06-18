# sources/user-network-fs/samba/source4/lib/policy/gp_manage.c

`gp_manage.c` orchestrates higher-level Group Policy management across LDAP and SYSVOL. `gp_ads_to_dir_access_mask()` maps directory-service ACE access bits to filesystem directory rights. `gp_create_gpt_security_descriptor()` converts a DS security descriptor to a GPT filesystem descriptor, copying owner/group/SACL, transforming DACL ACEs, skipping `SID_BUILTIN_PREW2K` allow ACEs, and adding inheritance flags. `gp_create_gpo()`, `gp_set_acl()`, and `gp_push_gpo()` combine LDAP and filesystem helpers.

`gp_create_gpo()` generates an uppercase GUID name, builds a SYSVOL path, creates the GPT, creates the LDAP GPC, refetches the GPO security descriptor, converts it to filesystem form, and applies it to SYSVOL. `gp_set_acl()` writes LDAP ACL first, then mirrors the resulting descriptor to SYSVOL. `gp_push_gpo()` parses GPT.INI, pushes local GPT files, and updates LDAP metadata.

Persistence spans both AD and SYSVOL, but operations are not transactional across those stores. Failures can leave an LDAP GPC without files, files without matching LDAP state, or mismatched ACLs. Additional risks include assuming `ds_sd->dacl` is non-NULL, broad access-mask mapping, and the unused GPT.INI filename in `gp_push_gpo()`. Tests should cover partial failures, descriptor conversion, GUID/path creation, and LDAP/SYSVOL consistency.
