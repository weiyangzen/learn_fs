
# sources/user-network-fs/rclone/fstest/testserver/images/test-hdfs/run.sh

Purpose: container entrypoint for the HDFS test image.

Important APIs/types/functions: reads `KERBEROS` env flag; when true it creates a Kerberos database, admin/user principals, HDFS/HTTP service principals, keytab, starts KDC, and obtains a user ticket. When false it removes Kerberos-marked config blocks from core/hdfs site files. It then formats the namenode and launches namenode and datanode.

Control flow: Kerberos conditional setup, config mutation, `hdfs namenode -format test`, background namenode/datanode, then `exec sleep infinity` to keep the container alive.

State/persistence: mutates config files in-place, creates Kerberos DB/keytab/ticket cache, and initializes HDFS data directories in the container.

Dependencies/integration: invoked by Docker `CMD`; `TestHdfs` maps ports and may copy the Kerberos ccache from the container.

Risks: fixed passwords and repeated namenode formatting are appropriate only for disposable containers. A fixed sleep/daemon startup model can be timing-sensitive.

Test signals: exposed HDFS port accepts connections; with Kerberos, copied ticket cache enables authenticated rclone HDFS access.
