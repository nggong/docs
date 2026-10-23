# Get GitHub Notifications in Slack

This guide configures the official GitHub app for Slack to report activity from repositories in the `nggong`
organization on GitHub.com.
It covers personal attention notifications and optional repository notifications, including GitHub Actions workflow runs.

## Understand the Notification Model

The GitHub app sends notifications to the Slack conversation where a subscription was created.
That conversation can be a channel or your direct message with the GitHub app.

Personal attention notifications are not an independent organization-wide feed.
They are Slack mentions attached to notifications from subscribed repositories.
GitHub documents these attention cases:

- assignment to an issue;
- a pull request review request;
- a mention in an issue, pull request, comment, or discussion;
- a deployment review request; and
- a scheduled pull request review reminder.

GitHub calls tickets **issues**.
GitHub's documentation does not list assignment to a pull request as an attention case.
Use a review request or an explicit mention when a Slack notification is important.

## Prerequisites

Before you start:

- The official GitHub app must be installed in the Slack workspace. (This has already been done for the NSO Slack
  workspace.)
- The app must have access to the required repositories in the `nggong` GitHub organization. (This has already been
  done for the NSO Slack workspace and the `nggong` GitHub organization.)
- You must have access to those repositories through your GitHub account.

If the app is not available or cannot access a required repository, ask a Slack workspace administrator or GitHub
organization owner to review the integration configuration.

## Connect Your GitHub and Slack Accounts

1. In Slack, open a direct message with the **GitHub** app.
2. Follow the app's prompt to connect your GitHub account.
3. Sign in to the GitHub account that you use for ngGONG work.
4. Review and approve the requested access.

If the connection prompt is not present, enter this command in the direct message:

```text
/github signin
```

The connection lets GitHub map your GitHub identity to your Slack identity.
Without it, Slack cannot identify you in repository notifications.

If you connect the GitHub app in more than one Slack workspace, GitHub mentions work only in the workspace where you
most recently signed in.

## Subscribe to Personal Attention Notifications

Create personal subscriptions in your direct message with the GitHub app.
For example, subscribe to the documentation repository:

```text
/github subscribe nggong/docs
```

Repeat the command for each ngGONG repository where you want attention notifications.
GitHub's current documented command subscribes one Slack conversation to one repository; it does not document an
organization-wide wildcard subscription.

A basic repository subscription also sends the repository's default event set to the direct message.
This can produce more messages than only the ones that mention you.
Review the result before subscribing to many active repositories.

List the repositories subscribed in the current Slack conversation:

```text
/github subscribe list
```

List the enabled features and filters:

```text
/github subscribe list features
```

After setup, ask another developer to mention you in a test issue or request your review on a test pull request.
Confirm that Slack identifies you in the resulting notification.

## Send Repository Notifications to a Channel

Repository subscriptions belong to the Slack conversation where you create them.
To notify a team channel:

1. Open the target Slack channel.
2. For a private channel, add the GitHub app:

   ```text
   /invite @github
   ```

3. Subscribe the channel to the repository:

   ```text
   /github subscribe nggong/docs
   ```

By default, a repository subscription includes issue and pull request state changes, commits to the default branch,
releases, and deployments.
The exact active feature list is available through `/github subscribe list features`.

## Add GitHub Actions Notifications

The `workflows` feature is not enabled by a basic repository subscription.
Enable it in the Slack direct message or channel where the notifications must appear:

```text
/github subscribe nggong/docs workflows
```

Without a filter, GitHub configures workflow notifications for pull requests that target the repository's default branch.
To include pull request and `main` branch workflow runs for `nggong/docs`, use:

```text
/github subscribe nggong/docs workflows:{event:"pull_request","push" branch:"main"}
```

The app can request additional GitHub permissions the first time that someone enables workflow notifications for the
organization.
Follow the prompt or ask a GitHub organization owner to approve the request.

The built-in `workflows` subscription reports workflow starts and completions.
It does not provide a documented filter for failed runs only.
If a channel must receive only failures, add explicit Slack notification logic to the GitHub Actions workflow after the
team agrees on the destination, credentials, and secret-management approach.

Disable workflow notifications with:

```text
/github unsubscribe nggong/docs workflows
```

## Enable Other Repository Events

Use the same pattern for other optional events:

```text
/github subscribe OWNER/REPOSITORY reviews
/github subscribe OWNER/REPOSITORY comments
/github subscribe OWNER/REPOSITORY discussions
/github subscribe OWNER/REPOSITORY branches
/github subscribe OWNER/REPOSITORY commits:*
```

You can enable more than one feature in a command:

```text
/github subscribe nggong/docs reviews comments
```

To disable features without removing the full repository subscription:

```text
/github unsubscribe nggong/docs reviews comments
```

Adding comments or reviews to a busy channel can create substantial noise.
Enable only the events that the channel is expected to act on.

## Troubleshooting

### Slack does not recognize `/github`

The GitHub app is not installed in the workspace or is not available in the current conversation.
Ask a Slack workspace administrator for help.

### A private channel receives no notifications

Invite the GitHub app to the channel with `/invite @github`, then check the subscription with
`/github subscribe list`.

### A private repository cannot be subscribed

The GitHub app may not have access to that repository.
Ask a GitHub organization owner to review the app installation and repository access.

### Other users are mentioned, but you are not

Run `/github signin` and connect the correct GitHub account.
If you use more than one Slack workspace, confirm that this is the workspace where you most recently connected the app.

### Expected workflow runs do not appear

Check the subscription with `/github subscribe list features`.
Confirm that its workflow filters match the workflow event and branch.
The unfiltered `workflows` subscription does not cover every possible workflow run.

## References

- [GitHub: Integrate GitHub with Slack]
- [GitHub: Use GitHub in Slack]
- [GitHub: Customize Slack notifications]
- [GitHub: Permissions for the Slack integration]

[GitHub: Integrate GitHub with Slack]:
  https://docs.github.com/en/integrations/how-tos/slack/integrate-github-with-slack
[GitHub: Use GitHub in Slack]:
  https://docs.github.com/en/integrations/how-tos/slack/use-github-in-slack
[GitHub: Customize Slack notifications]:
  https://docs.github.com/en/integrations/how-tos/slack/customize-notifications
[GitHub: Permissions for the Slack integration]:
  https://docs.github.com/en/integrations/reference/slack-permissions
