# sources/object-store/apache-ozone/hadoop-ozone/client/src/main/java/org/apache/hadoop/ozone/client/io/KeyCommitOutput.java

Purpose: This package-private interface captures commit-time operations common to key output implementations that also expose key metadata.

Important APIs and types: It extends `KeyMetadataAware` and declares `setPreCommits(List<CheckedRunnable<IOException>>)` plus `getCommitUploadPartInfo`. The pre-commit hook type comes from Ratis and can throw `IOException`; multipart commit info is `OmMultipartCommitUploadPartInfo`.

Control flow: Wrappers such as `OzoneOutputStream` and `OzoneDataStreamOutput` detect this interface and install pre-commit callbacks before the underlying key stream closes and commits to OM.

State and persistence behavior: The interface has no state. Implementations store pre-commit hooks and expose multipart upload part commit results after OM commit.

Dependencies and integration points: Implemented by `KeyOutputStream` and `KeyDataStreamOutput`; EC output inherits the same commit contract. It is the bridge between public wrapper streams and internal key commit implementations.

Risks: Since it is package-private, only same-package wrappers can rely on it. Hook order and exception behavior are implementation-specific but affect whether OM commit occurs.

Test signals: Tests should verify wrappers find `KeyCommitOutput` through direct and encrypted streams, pre-commit hooks run before commit, exceptions prevent commit, and multipart commit info is returned after close.
