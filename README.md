# Memo-CLI

A terminal application to help you remember and track usage of command-line shortcuts and aliases with flashcard-like features.

## Installation

```bash
pip install .
```

## Usage

### Add a command
```bash
memo add "ls -la" --desc "List all files including hidden ones"
```

### Add via pipe
```bash
echo "git status" | memo add
```

### List commands
```bash
memo list
```

### Search
```bash
memo search "list"
```

### Execute and track
```bash
memo exec 1
```

### Quiz mode
```bash
memo quiz
```

### Delete
```bash
memo delete 1
```
