# File Research: sources/os/bsd/netbsd-src/lib/libc/posix1e/acl_set.c

ACL setter and mutator functions. File, link, and fd setters normalize ACL type values, reject ACL/type brand mismatches, sort POSIX.1e ACLs before submission, reset the iterator cursor, and call the internal kernel set wrappers. `acl_set_fd()` selects NFSv4 versus access ACL based on `fpathconf()`.

Entry mutators set permission sets, qualifiers, tag types, and NFSv4 entry types. Permission setting brands entries as NFSv4 when NFSv4-only permission bits are used; tag and entry-type setters enforce brand compatibility and reject unknown values with `EINVAL`.
