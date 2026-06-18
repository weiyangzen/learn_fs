# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsprogs.8.in

## Role

`ntfsprogs.8.in` is the overview manual page for the ntfs-3g NTFS utility suite.

## Content Summary

It describes `ntfsprogs` as a shared-library-based suite of NTFS utilities and lists the major tools:

- creation and resize: `mkntfs`, `ntfsresize`
- inspection/listing: `ntfsinfo`, `ntfsls`, `ntfscluster`, `ntfscmp`
- data movement/copying: `ntfscat`, `ntfscp`
- repair/recovery: `ntfsfix`, `ntfsrecover`, `ntfsundelete`, `ntfsclone`
- mutation/wiping/truncation: `ntfslabel`, `ntfsfallocate`, `ntfstruncate`, `ntfswipe`

## Relationship To This Batch

This overview includes the normal tools researched here: `ntfsfix`, `ntfsinfo`, `ntfslabel`, `ntfsls`, and `ntfsrecover`. It does not mention quarantined developer utilities such as `ntfsmftalloc` and `ntfsmove`.

## Notes

The manpage is descriptive only; it contains no executable logic. It points readers to `ntfs-3g(8)` and the upstream project availability URL.
