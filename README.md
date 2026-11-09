<p align="center">
  <img src="docs/media/logo.svg" width="96" height="96" alt="">
</p>

<h1 align="center">memo</h1>

<p align="center">
  Flashcards for the shell commands you keep re-googling.
</p>

![Adding four commands to memo, listing them, then a quiz round](docs/media/demo.gif)

You finally find the incantation (`lsof -i :8080`, `du -sh * | sort -h`, that
`git log` flag combination) and three weeks later it's gone again. `memo` is
a small notebook for those commands that also quizzes you on them until they
stick.

## Features

- **Save a command** with a description, or pipe one in: `echo "rg -l TODO" | memo add`.
- **Man-page lookup:** leave out the description and memo offers the
  `whatis` summary for that command.
- **Quiz mode:** memo shows you the description, you type the command.
- **Run and count:** `memo exec <id>` runs a saved command and tracks how often
  you use it, so `memo list --sort tally` shows what you rely on.
- **Search** across commands and descriptions.
- Everything lives in a single JSON file at `~/.memo_cli/db.json`.

## Install

memo is a Python 3 package. The easiest way to get it on your `PATH` is
[pipx](https://pipx.pypa.io/):

```bash
pipx install git+https://github.com/stephenbreen/memo
```

Or from a clone, with plain pip:

```bash
git clone https://github.com/stephenbreen/memo.git
cd memo
pip install .
```

## Usage

```bash
memo add "ls -la" --desc "List all files including hidden ones"
echo "git status" | memo add          # read the command from a pipe
memo add "du -sh * | sort -h"         # no --desc: offers the man-page summary

memo list                             # --sort id | text | tally | last_used
memo search "port"
memo quiz                             # type 'exit' to stop early
memo exec 1                           # asks first, then runs it and bumps the tally
memo delete 1
```

Adding a command that's already saved offers to update its description
instead of creating a duplicate. `memo --help` and `memo <command> --help`
list every option.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

The demo GIF is recorded with [VHS](https://github.com/charmbracelet/vhs) in a
throwaway `HOME`, so your own command list never ends up in it:

```bash
vhs docs/demo.tape
```

## License

MIT, see [LICENSE](LICENSE).

---

<sub>Made by [Stephen Breen](https://stephenbreen.github.io).</sub>
