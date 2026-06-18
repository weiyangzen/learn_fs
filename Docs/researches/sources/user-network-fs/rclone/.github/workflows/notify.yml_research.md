# sources/user-network-fs/rclone/.github/workflows/notify.yml

Purpose: Sends notifications when issues receive configured labels.

Important APIs/types/functions: Workflow triggers on `issues` labeled events. Job uses `jenschelkopf/issue-label-notification-action@1.3` with `NOTIFY_ACTION_TOKEN` and recipient mapping `Support Contract=@rclone/support`.

Control flow: When an issue is labeled, the action reads label-recipient mappings and notifies the matching team/user.

State and persistence: No repository artifacts; side effect is notification delivery through GitHub/action mechanisms.

Dependencies and integration points: Depends on GitHub issue label events, an external action, token secret, and the `@rclone/support` recipient.

Risks: Misconfigured or missing token prevents notification. Label text must match exactly.

Test signals: Manual issue labeling is the practical validation path.
