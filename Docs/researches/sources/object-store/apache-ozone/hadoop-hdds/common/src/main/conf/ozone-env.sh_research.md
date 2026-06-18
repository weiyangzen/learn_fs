## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/conf/ozone-env.sh

**Purpose:** Shell environment template for Ozone commands and daemons, documenting and defaulting runtime environment variables for Java, classpath, logs, SSH fanout, daemon options, privileged execution, direct memory caps, and command-specific JVM options.

**Important APIs/types/functions:** The only active logic enables core dumps only when the hard core limit is non-zero, suppressing errors, and exports `OZONE_OS_TYPE` from `uname -s` if unset. The rest is commented configuration guidance for `JAVA_HOME`, `OZONE_HOME`, `OZONE_CONF_DIR`, heap sizes, `OZONE_OPTS`, client/server/daemon command opts, classpath handling, SSH options, worker host lists, log/pid directories, security logger, policy file, JSVC settings, Netty/Ratis Netty direct memory caps, component-specific options, build paths, and user locks.

**Control flow:** Sourced by Ozone shell launch scripts. Active commands run during shell initialization before command dispatch; commented exports become active only when operators edit or override them.

**State and persistence:** Persistent shell configuration template. Runtime state is environment variables inherited by Ozone processes.

**Dependencies and integration points:** Integrates with Ozone shell functions and daemon launch scripts, Java runtime, Hadoop logging properties, SSH/pdsh orchestration, JSVC, Netty, Ratis shaded Netty, and service policy files.

**Risks:** Shell syntax must remain portable enough for supported launch environments. Incorrect edits can affect every Ozone command. The core dump logic deliberately avoids noisy failures in containers. Direct-memory cap values require raw bytes because Netty parsers do not accept suffixes.

**Test signals:** Usually validated by packaging and shell command smoke tests rather than JUnit. Manual `ozone version`/daemon starts are important for changes here.
