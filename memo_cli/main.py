import sys
import os
import subprocess
import random
import typer
import re
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from typing import Optional, List
from datetime import datetime
from memo_cli.storage import Database

app = typer.Typer(help="Memo-CLI: Shortcut recall and tracking tool.")
console = Console()
db = Database()

def fetch_man_description(command_text: str) -> Optional[str]:
    """
    Attempt to fetch a short description from the system man pages.
    """
    if not command_text:
        return None
    
    # Get the base command (first word)
    base_command = command_text.split()[0]
    # Remove path if present
    base_command = os.path.basename(base_command)

    try:
        # Try whatis first
        result = subprocess.run(["whatis", base_command], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            # 1. Look for exact match in section 1 (user commands)
            for line in lines:
                if re.search(rf"^{re.escape(base_command)}\(1\)", line):
                    match = re.search(r"\s+-\s+(.+)$", line)
                    if match:
                        return match.group(1).strip()
            
            # 2. Look for any exact match in any section
            for line in lines:
                if re.search(rf"^{re.escape(base_command)}\(\d\)", line):
                    match = re.search(r"\s+-\s+(.+)$", line)
                    if match:
                        return match.group(1).strip()
            
            # 3. Fallback to any line that has the command(section)
            for line in lines:
                if re.search(rf"\b{re.escape(base_command)}\(\d\)", line):
                    match = re.search(r"\s+-\s+(.+)$", line)
                    if match:
                        return match.group(1).strip()
    except Exception:
        pass
    
    return None

@app.command()
def add(
    command_text: Optional[str] = typer.Argument(None, help="The command or shortcut to store."),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Description of the command."),
    tags: Optional[List[str]] = typer.Option(None, "--tag", "-t", help="Tags for categorization.")
):
    """
    Store a new command and its description.
    If piped, command text is read from stdin.
    If description is missing, it tries to fetch it from man pages.
    """
    if command_text is None and not sys.stdin.isatty():
        # Read from pipe
        command_text = sys.stdin.read().strip()
        if not command_text:
            console.print("[red]Error: Empty input from pipe.[/red]")
            raise typer.Exit(1)
        console.print(f"Adding command from pipe: [green]{command_text}[/green]")
    
    if not command_text:
        command_text = Prompt.ask("Enter the command/shortcut")
    
    # Check if the command already exists
    existing_cmd = db.get_command_by_text(command_text)
    if existing_cmd:
        console.print(f"[yellow]Command '[bold]{command_text}[/bold]' is already in your list (ID: {existing_cmd.id}).[/yellow]")
        console.print(f"Current Description: [dim]{existing_cmd.description}[/dim]")
        if Confirm.ask("Do you want to update its description/tags instead?"):
            if not description:
                description = Prompt.ask("Enter new description", default=existing_cmd.description)
            # We don't have an update_command method yet, but we can reuse delete and add or add an update method
            # For simplicity let's add an update method to storage.py later or just modify here
            db.table.update({"description": description, "tags": tags or existing_cmd.tags}, doc_ids=[existing_cmd.id])
            console.print("[bold green]Updated successfully![/bold green]")
            return
        else:
            console.print("[blue]Keeping original entry.[/blue]")
            return

    if not description:
        # Try to fetch from man pages
        man_desc = fetch_man_description(command_text)
        if man_desc:
            console.print(f"Found description via man: [dim]{man_desc}[/dim]")
            if Confirm.ask("Use this description?", default=True):
                description = man_desc
        
    if not description:
        description = Prompt.ask(f"Enter description for '{command_text}'")
    
    doc_id = db.add_command(text=command_text, description=description, tags=tags)
    console.print(f"[bold green]Stored![/bold green] (ID: {doc_id})")

@app.command()
def list(
    sort_by: str = typer.Option("id", "--sort", "-s", help="Sort by: id, text, tally, last_used.")
):
    """
    List all stored commands.
    """
    commands = db.list_commands()
    if not commands:
        console.print("[yellow]No commands stored yet.[/yellow]")
        return

    if sort_by == "text":
        commands.sort(key=lambda x: x.text.lower())
    elif sort_by == "tally":
        commands.sort(key=lambda x: x.tally, reverse=True)
    elif sort_by == "last_used":
        commands.sort(key=lambda x: (x.last_used or datetime.min), reverse=True)
    else:
        commands.sort(key=lambda x: x.id)

    table = Table(title="Stored Commands")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Command", style="green")
    table.add_column("Description", style="white")
    table.add_column("Tally", justify="center", style="magenta")
    table.add_column("Last Used", style="dim")

    for cmd in commands:
        last_used_str = cmd.last_used.strftime("%Y-%m-%d %H:%M") if cmd.last_used else "Never"
        table.add_row(
            str(cmd.id),
            cmd.text,
            cmd.description,
            str(cmd.tally),
            last_used_str
        )

    console.print(table)

@app.command()
def search(query: str = typer.Argument(..., help="Search query (text or description)")):
    """
    Search for a stored command.
    """
    results = db.search_commands(query)
    if not results:
        console.print(f"[yellow]No results found for '{query}'.[/yellow]")
        return

    table = Table(title=f"Search Results for '{query}'")
    table.add_column("ID", justify="right", style="cyan")
    table.add_column("Command", style="green")
    table.add_column("Description", style="white")
    table.add_column("Tally", justify="center", style="magenta")

    for cmd in results:
        table.add_row(str(cmd.id), cmd.text, cmd.description, str(cmd.tally))

    console.print(table)

@app.command()
def exec(command_id: int = typer.Argument(..., help="ID of the command to execute")):
    """
    Execute a stored command and increment its tally.
    """
    cmd = db.get_command(command_id)
    if not cmd:
        console.print(f"[red]Error: Command with ID {command_id} not found.[/red]")
        raise typer.Exit(1)

    console.print(f"Executing: [bold green]{cmd.text}[/bold green]")
    if Confirm.ask("Proceed?"):
        try:
            # We use shell=True to support aliases/shell built-ins if needed
            # But normally it's just a subprocess.
            subprocess.run(cmd.text, shell=True, check=True)
            db.update_tally(command_id)
            console.print("[dim]Tally updated.[/dim]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Command failed with exit code {e.returncode}[/red]")
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")

@app.command()
def quiz():
    """
    Flashcard mode: Quiz yourself on your shortcuts.
    """
    commands = db.list_commands()
    if not commands:
        console.print("[yellow]No commands to quiz on. Add some first![/yellow]")
        return

    random.shuffle(commands)
    score = 0
    total = len(commands)

    console.print("[bold blue]--- Shortcut Quiz Mode ---[/bold blue]")
    console.print(f"Total commands: {total}")
    console.print("Type 'exit' to quit at any time.\n")

    for i, cmd in enumerate(commands, 1):
        console.print(f"Q{i}/{total}: [bold cyan]{cmd.description}[/bold cyan]")
        user_input = Prompt.ask("What's the command?").strip()

        if user_input.lower() == "exit":
            break

        if user_input == cmd.text:
            console.print("[bold green]Correct![/bold green] 🎉")
            score += 1
        else:
            console.print(f"[bold red]Wrong.[/bold red] The correct command is: [bold green]{cmd.text}[/bold green]")
        
        console.print()

    console.print(f"[bold blue]Quiz finished![/bold blue] Final Score: {score}/{total}")

@app.command()
def delete(command_id: int = typer.Argument(..., help="ID of the command to delete")):
    """
    Remove a command from the database.
    """
    cmd = db.get_command(command_id)
    if not cmd:
        console.print(f"[red]Error: Command with ID {command_id} not found.[/red]")
        return

    if Confirm.ask(f"Are you sure you want to delete '{cmd.text}'?"):
        db.delete_command(command_id)
        console.print("[green]Deleted.[/green]")

if __name__ == "__main__":
    app()
