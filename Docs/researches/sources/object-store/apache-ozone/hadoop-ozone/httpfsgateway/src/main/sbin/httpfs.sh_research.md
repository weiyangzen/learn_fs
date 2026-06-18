# sources/object-store/apache-ozone/hadoop-ozone/httpfsgateway/src/main/sbin/httpfs.sh

## Purpose
`httpfs.sh` is a deprecated compatibility launcher for the HttpFS server. It forwards commands to `hdfs`.

## Important APIs, types, and functions
`print_usage` emits `run|start|status|stop` usage. The script maps `run` to `hdfs httpfs` and `start|stop|status` to `hdfs --daemon <command> httpfs`. It locates `hdfs` under `$HADOOP_HOME/bin` or relative `../bin`.

## Control flow
The script prints a deprecation warning, validates arguments, translates the subcommand, resolves the binary directory, and `exec`s `hdfs` with translated arguments.

## State and persistence behavior
It does not persist state. Daemon state is managed by the delegated `hdfs` command.

## Dependencies and integration points
It depends on Bash and a Hadoop installation layout. It preserves older operational entrypoints while directing users to `hdfs [--daemon ...] httpfs`.

## Risks and edge cases
If neither `$HADOOP_HOME/bin/hdfs` nor relative `../bin/hdfs` exists, exec fails. Unknown commands exit 1. Zero arguments print usage and exit with the shell default success status from `exit`.

## Test signals
Shell command tests would verify argument translation and deprecation output; none are in this subset.
