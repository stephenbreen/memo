# Records docs/media/demo.gif. Needs `memo` on your PATH and vhs installed:
#   pipx install -e . && vhs docs/demo.tape
# Uses a throwaway HOME so your real ~/.memo_cli is never touched.
Output docs/media/demo.gif

Set Shell "bash"
Set FontFamily "Menlo"
Set FontSize 18
Set Width 1400
Set Height 560
Set Padding 24
Set Theme "Catppuccin Mocha"
Set TypingSpeed 35ms

Hide
Type 'export HOME="$(mktemp -d)" PYTHONPATH="$PWD/docs/demo" PS1="$ " && clear'
Enter
Sleep 300ms
Show

Type 'memo add "git log --oneline --graph --all" -d "Branch graph of every ref"'
Enter
Sleep 1.2s
Type 'memo add "lsof -i :8080" -d "What is holding port 8080?"'
Enter
Sleep 1.2s
Type 'echo "rg -l TODO" | memo add -d "Files that still have a TODO"'
Enter
Sleep 1.2s

# No description: memo looks it up in the man pages
Type 'memo add "du -sh * | sort -h"'
Enter
Sleep 1.5s
Enter
Sleep 1.2s

Type "clear && memo list"
Enter
Sleep 3s

Type "clear && memo quiz"
Enter
Sleep 1.5s
Type "du -sh * | sort -h"
Sleep 400ms
Enter
Sleep 1.5s
Type "netstat -an | grep 8080"
Sleep 400ms
Enter
Sleep 2s
Type "exit"
Sleep 400ms
Enter
Sleep 2.5s
