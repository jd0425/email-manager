# Gmail + Calendar access — setup

This whole document is for the **live-connector** path (see the
Prerequisite section in `SKILL.md`) — ongoing, hands-off access to a real
mailbox. If the user just wants to try the triage/catalog workflow on a
batch of exported or forwarded email first, none of this setup is needed;
skip straight to the batch triage procedure in `SKILL.md` and come back
here when they're ready for live access.

This documents how to wire up Gmail/Calendar access for this skill using the
[Google Workspace MCP server](https://github.com/taylorwilsdon/google_workspace_mcp)
(`workspace-mcp` on PyPI), running locally in stdio mode. These are real
steps verified against the actual package, not paraphrased from its docs —
where its own README was ambiguous (transport/redirect details), this was
checked directly against the installed source instead.

If the user's mail isn't Gmail, the shape of this setup — an MCP server
with OAuth against the provider, registered locally, scoped permissions
short of "send" — still applies; swap in whatever MCP/API exists for their
provider and adapt accordingly.

## What you need installed

- `uv`/`uvx` (e.g. via Homebrew: `brew install uv`) — runs `workspace-mcp`
  without a manual Python venv.
- On macOS, `openssl@3` + `pkg-config` (e.g. `brew install openssl@3
  pkg-config`) — `workspace-mcp` depends on `cryptography`, which can fail
  to build from source without these if no prebuilt wheel matches the
  machine. Without them, the first `uvx workspace-mcp` run tends to fail
  with a `cryptography` / `maturin` / "Could not find directory of OpenSSL
  installation" error. Install these first if that happens.

## 1. Google Cloud OAuth client (the user has to do this part — needs their Google login)

1. Go to console.cloud.google.com and create a new project (any name).
2. **APIs & Services → Library** — enable:
   - **Gmail API**
   - **Google Calendar API**
3. **APIs & Services → OAuth consent screen**
   - User type: **External**.
   - App name: anything.
   - Add the target Gmail address as a **test user** — personal Gmail
     accounts stay in "Testing" mode, which is fine; it still works, but
     shows an "unverified app" warning on first login (click Advanced →
     "Go to (app name)" to proceed past it).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID**
   - Application type: **Desktop app** — this is the correct type for
     this server's stdio mode. It runs its own local callback server on
     `http://localhost:8000/oauth2callback`, and Desktop-type clients are
     allowed by Google to redirect to any localhost port without
     pre-registering it.
   - Copy the **Client ID** and **Client Secret** shown.

## 2. Register the MCP server

```bash
claude mcp add gmail-workspace \
  -e GOOGLE_OAUTH_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com" \
  -e GOOGLE_OAUTH_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
  -- /usr/local/bin/uvx workspace-mcp --permissions gmail:drafts calendar:full
```

Notes on the flags:
- `gmail:drafts` is cumulative: readonly + labels/archive/trash
  ("organize") + compose drafts. It deliberately stops short of
  `gmail:send` — Claude can read, file, and draft replies, but **cannot
  send mail on its own**. Anything that should be sent gets left as a
  draft for the user to review and send themselves. Loosen this only if
  the user explicitly wants Claude sending mail unattended.
- `calendar:full` grants create/update on the calendar (needed for bill
  and appointment reminders).
- `--permissions` and `--tools` are mutually exclusive on the CLI — use
  `--permissions service:level ...` only.

Restart the Claude session after adding the server so it picks up the new
MCP connection.

## 3. First-time auth

The first Gmail/Calendar tool call opens the default browser to Google's
consent screen and spins up a throwaway local server on port 8000 to catch
the redirect. Approve access for the scopes above. Tokens are then cached
locally (under `~/.google_workspace_mcp/credentials/` in the reference
setup) — re-auth shouldn't be needed again unless the token is revoked.

## Verifying it's working

```bash
claude mcp list
```
should show the server connected. If not, check its local logs (e.g.
`~/.google_workspace_mcp/logs/`) for errors.

## Re-authenticating mid-session

Testing-mode Google Cloud OAuth apps issue refresh tokens that expire after
a period of inactivity (roughly a week in practice) — expect an
`invalid_grant: Token has been expired or revoked` error periodically. When
a Gmail/Calendar tool call returns an auth-required error:

- **Don't just relay the auth URL through chat for a human to click.** The
  local OAuth callback server is short-lived and scoped to that one tool
  call — by the time someone reads the URL, opens a browser, and clicks
  through Google's consent screens, the local server has often already
  shut down, producing a confusing "can't connect to server" / "invalid or
  expired OAuth state" error even on a careful retry.
- **If a browser-automation MCP is available and already signed into the
  target account**, drive the same URL through that instead — navigate to
  the authorization URL from the error, click through the "hasn't been
  verified" warning → account chooser → consent screen. That's usually
  fast enough for the local callback server to still be listening.
  Otherwise, walk the human through clicking fast, or re-run the flow with
  them watching so the redirect completes promptly.
- After the callback confirms the token exchange succeeded, retry the
  original tool call directly.

## Multiple accounts

To triage more than one mailbox (a personal Gmail plus a work Gmail, say),
register a **separate MCP server instance per account** rather than trying
to reuse one connection across accounts — this server authenticates as a
single user per running instance. This is real, documented behavior of
`workspace-mcp` (not a workaround): it exposes `WORKSPACE_MCP_CREDENTIALS_DIR`
specifically so multiple local instances can keep separate credential
caches, and `USER_GOOGLE_EMAIL` to pin each instance to one account.

```bash
# Personal account
claude mcp add gmail-personal \
  -e GOOGLE_OAUTH_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com" \
  -e GOOGLE_OAUTH_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
  -e WORKSPACE_MCP_CREDENTIALS_DIR="$HOME/.google_workspace_mcp/personal" \
  -e USER_GOOGLE_EMAIL="personal@gmail.com" \
  -- /usr/local/bin/uvx workspace-mcp --permissions gmail:drafts calendar:full

# Work account
claude mcp add gmail-work \
  -e GOOGLE_OAUTH_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com" \
  -e GOOGLE_OAUTH_CLIENT_SECRET="YOUR_CLIENT_SECRET" \
  -e WORKSPACE_MCP_CREDENTIALS_DIR="$HOME/.google_workspace_mcp/work" \
  -e USER_GOOGLE_EMAIL="work@company.com" \
  -- /usr/local/bin/uvx workspace-mcp --permissions gmail:drafts calendar:full
```

Notes:
- The same Google Cloud OAuth client (Client ID/Secret) can be reused across
  accounts — it's the credentials *directory* and `USER_GOOGLE_EMAIL` that
  need to differ per instance, not the OAuth app itself. Each account still
  goes through its own first-time consent screen (step 3 above) the first
  time a tool call hits that server.
- Give each registered server a distinct, memorable name (`gmail-personal`,
  `gmail-work`) — that name is what tool calls route through, and it's how
  you tell the two mailboxes apart when triaging.
- This covers the common personal case (one person, a few of their own
  accounts). If the goal is instead hosting this centrally for a whole
  organization, `workspace-mcp` has a separate multi-tenant deployment mode
  (OAuth 2.1 with bearer tokens, or service-account domain-wide delegation)
  documented in its [deployment guide](https://workspacemcp.com/docs/deployment)
  — that's a different, heavier setup than a single user needs for their
  own two or three inboxes.
- See `references/schema.md` for how to reflect the account in
  `catalog.csv` once multiple connectors are wired up.

## Gotchas

- `cryptography` build failure on first `uvx workspace-mcp` run — see the
  Homebrew install step above.
- `--permissions` and `--tools` are mutually exclusive on the CLI.
- The project's own quick-start docs describe a hosted multi-tenant
  deployment with a web-application OAuth client and streamable-http
  transport — that's a different, more complex path than a single local
  user needs. Stick to stdio mode + a Desktop OAuth client as above.
