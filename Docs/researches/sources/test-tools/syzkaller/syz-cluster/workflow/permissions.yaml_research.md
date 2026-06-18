## sources/test-tools/syzkaller/syz-cluster/workflow/permissions.yaml

This RBAC `Role` named `executor` grants `create` and `patch` on Argo `workflowtaskresults`. It supports Argo executors recording task results.

The file is only a Role, not a RoleBinding, so integration requires binding it to the workflow service account elsewhere. Risks include insufficient permissions if the binding is missing and namespace scoping by whichever namespace applies the role.
