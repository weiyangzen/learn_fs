## sources/security-integrity/attr/xattr.conf

Purpose: default policy for xattr copy helpers.

It maps attribute-name patterns to `permissions` or `skip`, marking POSIX/NFS ACLs as permission-related and excluding kernel/security/indexing/filesystem-specific metadata such as SGI, EVM, AFS, and Beagle attributes. State is installed system configuration read lazily by `attr_copy_action`. Dependencies are `fnmatch` pattern semantics. Risks include policy order/precedence because parser prepends entries, local admin edits affecting library behavior process-wide, and stale defaults for new security xattrs. Test signal is `attr_copy_file` behavior against representative names.
