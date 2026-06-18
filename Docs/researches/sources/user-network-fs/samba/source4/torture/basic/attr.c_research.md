# sources/user-network-fs/samba/source4/torture/basic/attr.c

## Purpose
This file tests Windows file attribute behavior for SMB opens and setattr/getattr operations. It covers how truncate opens combine initial and requested attributes, and whether changing file/directory attributes preserves security descriptors.

## Important APIs, Types, And Functions
The public tests are `torture_openattrtest` and `torture_winattrtest`. Static tables `open_attrs_table` and `attr_results` define attribute combinations and expected truncate-open outcomes. The tests use `smbcli_nt_create_full`, `smbcli_setatr`, `smbcli_getatr`, `smb_raw_fileinfo` with `RAW_FILEINFO_SEC_DESC`, and `security_ace_equal`.

## Control Flow
`torture_openattrtest` iterates initial attribute combinations, creates a file, then iterates truncate-open attribute combinations and checks whether failures are `NT_STATUS_ACCESS_DENIED` unless the combination is listed as expected-success. Successful opens are closed and followed by `getatr` checks against `attr_results`. `torture_winattrtest` creates a file, stores its security descriptor, repeatedly sets attributes and confirms attributes and ACL ACEs remain stable, then repeats similar checks for a directory with `FILE_ATTRIBUTE_DIRECTORY` expected in returned attributes.

## State And Persistence
The tests create/delete `\openattr.file`, `\winattr1.file`, and `\winattr1.dir` on the target share. They modify file and directory attributes during execution and clean them up at exit labels.

## Dependencies And Integration Points
It depends on SMB client raw and convenience APIs, security descriptor structures, torture failure limits, and the basic suite that registers these tests. It exercises server create/open, attribute storage, descriptor retrieval, and directory handling.

## Risks And Test Signals
Risks include broad nested loops producing many failures, cleanup needing attribute reset before unlink, assumptions about archive bit normalization, and comparing ACE lists without first checking both DACL shapes in all cases. Passing tests signal Windows-compatible attribute preservation, truncate-open result attributes, directory attribute composition, and ACL stability across attribute changes.
