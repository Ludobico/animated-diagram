# Install animated-diagram (instructions for an AI agent)

You are an AI agent and the user asked you to install this skill. Follow these steps in order. Say what
you are about to run before you run it, and stop and ask whenever a step says so.

**Objective:** the skill folder `skills/animated-diagram/` (it holds `SKILL.md`) sits where the user's
agent loads skills from, and a smoke test passes.

**Done when:**
- `<skills dir>/animated-diagram/SKILL.md` exists and is readable.
- The smoke test in step 4 ends with `check.py` exit code 0.
- You have told the user how to start using it (step 5).

Source repository: `https://github.com/Ludobico/animated-diagram` (branch `main`).

## 1. Find out where the skill must go

Work out which agent the user wants this for. If it is not the one you are running in, or it is unclear,
ask.

| Agent | Personal (all projects) | Project only | How it loads |
|---|---|---|---|
| Claude Code (CLI, IDE extensions) | `~/.claude/skills/animated-diagram` | `<project>/.claude/skills/animated-diagram` | Picked up in the running session; new top-level folder → `/reload-skills` |
| Codex (CLI, IDE extension, app) | `~/.codex/skills/animated-diagram` (`$CODEX_HOME/skills`) | `<project>/.agents/skills/animated-diagram` | Detected automatically; if it does not show up, restart Codex. Type `$` or run `/skills` to pick it |
| Other agents that read Agent Skills (`SKILL.md` folders), e.g. Cursor, OpenCode | that agent's skills directory | that agent's project skills directory | See the agent's docs |
| Claude Desktop / claude.ai chat | cannot be installed by an agent: the user uploads a ZIP in Settings (step 3b) | — | — |

For agents other than Claude Code and Codex, use the skills directory that agent documents. If you do
not know it for certain, ask the user rather than guessing. On Windows, `~` is `%USERPROFILE%`.

Codex notes: both Codex paths above were checked on Codex CLI 0.165.0 on Windows (the skill was listed with
its name and description, and a junction was followed). OpenAI's docs also name `~/.agents/skills` as the
user-level folder. That one could not be checked on 0.165.0, so if `~/.codex/skills` is not picked up on a
newer Codex, try `~/.agents/skills`.

Default to the personal location unless the user wants it for one project only.

## 2. Get the files

Keep one clone in a stable place so the skill can be updated with `git pull`:

```bash
git clone --depth 1 https://github.com/Ludobico/animated-diagram.git ~/.animated-diagram
```

If `~/.animated-diagram` already exists, run `git -C ~/.animated-diagram pull` instead. If the user
already has a checkout of this repository, you may use it as the source instead of cloning.

## 3a. Link the skill folder (agents with a skills directory)

Link `<clone>/skills/animated-diagram` into the skills directory, so updates arrive with `git pull`:

```bash
# macOS / Linux
mkdir -p ~/.claude/skills
ln -s ~/.animated-diagram/skills/animated-diagram ~/.claude/skills/animated-diagram
```

```powershell
# Windows (a junction needs no admin rights)
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
New-Item -ItemType Junction -Path "$HOME\.claude\skills\animated-diagram" -Target "$HOME\.animated-diagram\skills\animated-diagram"
```

For Codex, link into `~/.codex/skills` the same way (`mkdir -p ~/.codex/skills`, or on Windows
`New-Item -ItemType Directory -Force "$HOME\.codex\skills"`).

Replace `~/.claude/skills` with the directory from step 1. If a link cannot be made, copy the folder
instead, and tell the user that updates then need a fresh copy. If `animated-diagram` already exists
there, ask before replacing it. If it is an old link, remove only the link (see "To uninstall" in
step 5); do not delete recursively through it.

## 3b. Claude Desktop / claude.ai chat

An agent cannot add a skill to the user's claude.ai account. Instead:
1. Make a ZIP whose root is the folder `animated-diagram/` (with `SKILL.md` inside), not the files on
   their own. Leave out `__pycache__`.
2. Give the ZIP to the user, with these steps: Settings → Capabilities → turn on "Code execution and file
   creation"; then Customize → Skills → "+" → "Create skill" → "Upload a skill" → choose the ZIP → turn
   the skill on. On Team or Enterprise plans an owner may have to allow skills first.
3. Tell the user that scripts run in Anthropic's cloud sandbox there. The animated SVG works, but a GIF
   needs a browser that the sandbox may not be able to download.

Then skip to step 5.

## 4. Check the runtime and run the smoke test

Requirements: Python 3.10+. GIF capture also needs Pillow and Playwright (`uv run` installs them from
the script header; without uv, `pip install pillow playwright`) and a browser (installed Chrome or Edge,
or `playwright install chromium`). Ask before installing packages or a browser.

Run the smoke test in a temporary folder, not inside the skill folder. `<skill>` is the installed
`animated-diagram` folder.

```bash
python <skill>/scripts/make_diagram.py <skill>/examples/mermaid-architecture.json out.svg --extra-icons <skill>/examples/icons/learning.py
python <skill>/scripts/check.py out.svg            # must exit 0
uv run <skill>/scripts/capture.py out.svg out.gif   # optional: needs the browser; produces a GIF
```

If `check.py` fails, report its output; do not edit the skill to make it pass. Delete the temporary
folder afterwards.

## 5. Report to the user

- Where the skill is installed, and whether it is a link (updates with `git -C ~/.animated-diagram pull`)
  or a copy.
- The smoke test result, and whether GIF capture works on this machine (and what is missing if not).
- How to use it: ask for something like "Turn this Mermaid diagram into an animated GIF" or "구조도를
  GIF로 만들어 줘". In Claude Code and Codex, `/skills` lists it. If it does not appear, start a new
  session (Codex: restart it).
- To uninstall: remove the link in the skills directory, then `~/.animated-diagram`. Remove the link
  itself, never its contents: `rm ~/.claude/skills/animated-diagram` (macOS / Linux) or
  `cmd /c rmdir "%USERPROFILE%\.claude\skills\animated-diagram"` (Windows); for Codex, use
  `.codex` in place of `.claude`. On Windows PowerShell 5.1,
  `Remove-Item -Recurse` on a junction can delete the files in the clone it points to.
