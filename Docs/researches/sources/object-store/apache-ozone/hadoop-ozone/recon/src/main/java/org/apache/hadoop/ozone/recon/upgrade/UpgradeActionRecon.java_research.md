# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/upgrade/UpgradeActionRecon.java

Purpose: `UpgradeActionRecon` is the runtime annotation used to associate a `ReconUpgradeAction` implementation with a `ReconLayoutFeature`.

Important APIs and types: retained at runtime and targeted at types. Its single element `feature()` returns the layout feature the annotated action should finalize.

Control flow and integration: `ReconLayoutFeature.registerUpgradeActions` scans the upgrade package for annotated classes, constructs them, reads the annotation, and attaches the action to the feature.

State and persistence: no runtime state beyond annotation metadata.

Dependencies: Java annotation APIs and `ReconLayoutFeature`.

Risks and test signals: action classes must have no-arg constructors for reflection. Tests should cover annotation discovery and feature binding.
