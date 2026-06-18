# sources/object-store/apache-ozone/hadoop-hdds/annotations/pom.xml

Purpose: Defines the `hdds-annotation-processing` Maven module. This module packages Apache Ozone compile-time annotation processors that validate internal annotations before the rest of the project compiles.

Important APIs/types/functions: The artifact is `org.apache.ozone:hdds-annotation-processing:2.3.0-SNAPSHOT`, packaged as a jar under the `hdds` parent. The module name and description identify it as annotation-processing tooling.

Control flow: Maven builds this module as an early dependency. The compiler plugin is configured with `<proc>none</proc>`, preventing the module's own processors from running while compiling the processors themselves.

State and persistence behavior: No runtime state. The persistent artifact is the jar containing processors and `META-INF/services` registrations.

Dependencies and integration points: Inherits dependencies and plugin configuration from the parent `hdds` project. The generated jar is later placed on javac's annotation processor path for other Ozone modules.

Risks: `<maven.test.skip>true</maven.test.skip>` means this module currently lacks direct test execution, so processor regressions can surface only when downstream modules compile. If service metadata is missing, processors silently will not run.

Test signals: Build-level signals are successful compilation of downstream modules with known-valid annotations and intentional invalid fixture annotations that fail compilation with the expected diagnostic messages.
