## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/scm/cert/CertRepair.java

Purpose: grouping command for SCM certificate-related repair operations.

Important APIs and control flow: picocli command `cert` registers `RecoverSCMCertificate` as the implementation subcommand. It contains no execution body.

State and dependencies: no direct state. It depends only on picocli metadata and the recover command class.

Risks and test signals: command registration drift is the primary risk. There are no certificate recovery tests in this subset; global dry-run metadata is checked by `TestOzoneRepair`.
