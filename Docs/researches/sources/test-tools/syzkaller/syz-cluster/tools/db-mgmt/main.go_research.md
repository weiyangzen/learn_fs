## sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/main.go

`db-mgmt` is an administrative CLI for creating/checking the Spanner database, running migrations, and executing ad hoc SQL. `runSQL` opens a Spanner client, executes a query, prints column names and values for each row, and closes resources.

`main` resolves the default Spanner URI, creates an emulator instance when `SPANNER_EMULATOR_HOST` is set, ensures the database exists, and then handles optional subcommands: `migrate` runs schema migrations, `run <SQL>` executes a query, and unknown commands fatal. With no subcommand it just verifies/create resources.

State changes target Spanner instance/database/schema. Integration points are local development, the migration Kubernetes job, and `pkg/db` migration code. Risks include unrestricted SQL execution, positional CLI parsing that only accepts the SQL as one argument, and fatal exits for admin workflows. There are no direct tests in this file.
