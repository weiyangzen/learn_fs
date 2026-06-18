<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.idmap.conf.in -->
# sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.idmap.conf.in

## Purpose

`cifs.idmap.conf.in` is a one-line request-key template for invoking `cifs.idmap`.

## Important APIs, Types, and Functions

The template line is `create cifs.idmap * * @sbindir@/cifs.idmap %k`, where `%k` is the key serial passed by request-key.

## Control Flow

Build substitution replaces `@sbindir@`; request-key later matches `cifs.idmap` key creation and executes the helper.

## State and Persistence Behavior

Installed under request-key configuration, this line controls kernel key upcall behavior. It does not store mapping state itself.

## Dependencies and Integration Points

It integrates Linux keyutils request-key with `cifs.idmap`.

## Risks and Edge Cases

Incorrect helper paths prevent CIFS ACL SID/ID mapping. The snippet assumes default request-key field ordering and wildcard constraints.

## Test Signals

Install in a test request-key configuration and trigger a `cifs.idmap` key request from a CIFS ACL mount or keyutils simulation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/cifs-utils/contrib/request-key.d/cifs.idmap.conf.in -->
