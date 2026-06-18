# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/package-info.java

Purpose: package documentation for `org.apache.hadoop.ozone.recon.tasks`.

Important APIs and types: declares package-level JavaDoc stating the package contains scheduled tasks used by Recon. It does not define runtime classes.

Control flow and integration: used by JavaDoc and package metadata only. It groups controller, task, event, and insight task classes.

State and persistence: none.

Dependencies: none.

Risks and test signals: no behavioral tests needed. Documentation should stay accurate as the package now includes async event buffering and upgrade-triggered reinitialization support, not only scheduled tasks.
