## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/scm/package-info.java

Purpose: package documentation for `org.apache.hadoop.ozone.recon.scm`.

Important APIs and types: no APIs are declared; it only supplies Javadoc package text.

Control flow: none.

State and persistence: none.

Dependencies and integration points: the package contains Recon's passive SCM facade, managers, handlers, storage config, policy provider, and sync helpers. The current package comment says the classes handle OM snapshot recovery and checkpoints, which appears stale for an SCM package.

Risks and edge cases: stale package documentation can mislead maintainers and generated docs. The actual package is SCM-oriented, not OM snapshot recovery.

Test signals: no tests apply directly. Documentation review should update the package description to match the SCM responsibilities.
