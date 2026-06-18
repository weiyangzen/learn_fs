# sources/security-integrity/selinux/libsemanage/src/users_join.c

## Purpose
Configures a joined database that presents base and extra user records as one `semanage_user_t`.

## APIs and integration
`SEMANAGE_USER_JOIN_RTABLE` points at `semanage_user_join()` and `semanage_user_split()`. `user_join_dbase_init()` combines two existing dbase configs with `dbase_join_init()`, while release delegates to `dbase_join_release()`.

## Risks and state
Correctness depends on both child databases sharing comparable keys and on join/split preserving name consistency. This file holds no state itself.
