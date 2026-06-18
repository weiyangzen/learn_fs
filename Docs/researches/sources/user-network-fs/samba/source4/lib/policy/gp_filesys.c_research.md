# sources/user-network-fs/samba/source4/lib/policy/gp_filesys.c

`gp_filesys.c` implements Group Policy Template (GPT) filesystem operations over the domain controller's `sysvol` SMB share. Important helpers include `gp_cli_connect()`, `gp_get_share_path()`, `gp_fetch_gpt()`, `gp_push_gpt()`, `gp_create_gpt()`, and `gp_set_gpt_security_descriptor()`. Internal list/copy helpers walk remote directories, copy files to local temporary policy directories, recursively push local files, and set NT security descriptors on GPT directories.

Control flow for fetch connects to `sysvol`, derives the share-relative path from a UNC `gPCFileSysPath`, lists remote entries recursively up to `GP_MAX_DEPTH`, creates local directories, and copies file contents while checking final size. Push does the reverse using local `opendir()` and SMB create/write calls. Create builds a local GPT skeleton with `User`, `Machine`, and `GPT.INI`, then uploads it.

Persistence spans local temp directories under `tmpdir()/policy` and remote SYSVOL contents. Risks include path parsing based on the fourth backslash, partial cleanup on copy failures, depth truncation, local case-sensitivity around `GPT.INI`, mkdir failures on preexisting directories, and ACL application only to the top GPT directory. Tests need live or fake SMB SYSVOL coverage for fetch, push, create, and security descriptor setting.
